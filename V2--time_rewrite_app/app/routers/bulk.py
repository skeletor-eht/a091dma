"""
Bulk operations router for CSV import/export
"""
import csv
import io
import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..models import (
    User,
    Client,
    TimeEntry,
    RewriteRecord,
    AuditEvent,
    BatchOperation,
    RewriteVersion,
)
from ..schemas import BatchOperationOut, CSVImportRow
from ..deps import get_current_user, check_client_access
from ..llm import rewrite_entry
from ..routers.rewrites import build_client_rules

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/import-csv", response_model=BatchOperationOut)
async def import_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Import CSV file with time entries for bulk rewriting.
    Expected CSV format:
    client_id,original,hours
    C001,"Reviewed email from client regarding contract",1.5
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")

    # Read CSV file
    contents = await file.read()
    csv_text = contents.decode('utf-8')
    csv_reader = csv.DictReader(io.StringIO(csv_text))

    # Validate headers
    required_headers = {'client_id', 'original', 'hours'}
    if not required_headers.issubset(csv_reader.fieldnames or []):
        raise HTTPException(
            status_code=400,
            detail=f"CSV must contain headers: {', '.join(required_headers)}"
        )

    # Parse all rows first
    rows = []
    for row in csv_reader:
        try:
            rows.append(CSVImportRow(
                client_id=row['client_id'].strip(),
                original=row['original'].strip(),
                hours=float(row['hours'])
            ))
        except (KeyError, ValueError) as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid CSV format: {str(e)}"
            )

    if not rows:
        raise HTTPException(status_code=400, detail="CSV file is empty")

    # Create batch operation record
    batch_id = str(uuid.uuid4())
    batch_op = BatchOperation(
        id=batch_id,
        user_id=current_user.id,
        operation_type="import",
        filename=file.filename,
        total_rows=len(rows),
        successful_rows=0,
        failed_rows=0,
        status="processing",
    )
    db.add(batch_op)
    db.commit()

    # Process each row
    errors = []
    successful = 0
    failed = 0

    for idx, row in enumerate(rows, start=1):
        try:
            # Check if user has access to this client
            if not check_client_access(current_user, row.client_id, db):
                errors.append(f"Row {idx}: No access to client {row.client_id}")
                failed += 1
                continue

            # Get client
            client = db.query(Client).filter(Client.id == row.client_id).first()
            if not client:
                errors.append(f"Row {idx}: Client {row.client_id} not found")
                failed += 1
                continue

            # Create time entry
            time_entry_id = str(uuid.uuid4())
            time_entry = TimeEntry(
                id=time_entry_id,
                client_id=row.client_id,
                original=row.original,
                hours=row.hours,
            )
            db.add(time_entry)

            # Generate rewrite
            rules = build_client_rules(client)
            rewrite_result = rewrite_entry(row.original, row.hours, rules)

            # Save rewrite
            rewrite_id = str(uuid.uuid4())
            rewrite_record = RewriteRecord(
                id=rewrite_id,
                time_entry_id=time_entry_id,
                standard=rewrite_result["standard"],
                client_compliant=rewrite_result["client_compliant"],
                audit_safe=rewrite_result["audit_safe"],
                notes=rewrite_result.get("notes", ""),
            )
            db.add(rewrite_record)

            # Save version history
            version = RewriteVersion(
                id=str(uuid.uuid4()),
                time_entry_id=time_entry_id,
                version_number=1,
                standard=rewrite_result["standard"],
                client_compliant=rewrite_result["client_compliant"],
                audit_safe=rewrite_result["audit_safe"],
                notes=rewrite_result.get("notes", ""),
                created_by=current_user.username,
                is_current=True,
            )
            db.add(version)

            # Create audit event
            audit_event = AuditEvent(
                id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                username=current_user.username,
                role=current_user.role,
                client_id=row.client_id,
                time_entry_id=time_entry_id,
                rewrite_id=rewrite_id,
                model_name="qwen2.5:7b",
                rules_snapshot=str(rules),
            )
            db.add(audit_event)

            successful += 1

        except Exception as e:
            errors.append(f"Row {idx}: {str(e)}")
            failed += 1

    # Update batch operation
    batch_op.successful_rows = successful
    batch_op.failed_rows = failed
    batch_op.status = "completed" if failed == 0 else "completed_with_errors"
    batch_op.error_log = "\n".join(errors) if errors else None
    batch_op.completed_at = datetime.utcnow()
    db.commit()

    return batch_op


@router.get("/export-csv")
async def export_csv(
    client_id: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export all rewrites to CSV.
    Optionally filter by client_id.
    """
    # Build query
    query = db.query(TimeEntry, RewriteRecord, Client).join(
        RewriteRecord, TimeEntry.id == RewriteRecord.time_entry_id
    ).join(
        Client, TimeEntry.client_id == Client.id
    )

    # Filter by client if specified
    if client_id:
        if not check_client_access(current_user, client_id, db):
            raise HTTPException(
                status_code=403,
                detail=f"No access to client {client_id}"
            )
        query = query.filter(TimeEntry.client_id == client_id)
    else:
        # Get all permitted clients
        from ..deps import get_user_permitted_clients
        permitted_ids = get_user_permitted_clients(current_user, db)
        query = query.filter(TimeEntry.client_id.in_(permitted_ids))

    results = query.all()

    # Create CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'client_id',
        'client_name',
        'original',
        'hours',
        'standard',
        'client_compliant',
        'audit_safe',
        'notes',
        'created_at'
    ])

    # Write data
    for time_entry, rewrite, client in results:
        writer.writerow([
            client.id,
            client.name,
            time_entry.original,
            time_entry.hours,
            rewrite.standard,
            rewrite.client_compliant,
            rewrite.audit_safe,
            rewrite.notes,
            time_entry.created_at.isoformat()
        ])

    # Create batch operation record
    batch_id = str(uuid.uuid4())
    batch_op = BatchOperation(
        id=batch_id,
        user_id=current_user.id,
        operation_type="export",
        filename=f"export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
        total_rows=len(results),
        successful_rows=len(results),
        failed_rows=0,
        status="completed",
        completed_at=datetime.utcnow(),
    )
    db.add(batch_op)
    db.commit()

    # Return CSV as download
    output.seek(0)
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition": f"attachment; filename={batch_op.filename}"
        }
    )


@router.get("/batch-operations", response_model=List[BatchOperationOut])
def list_batch_operations(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all batch operations for current user"""
    operations = db.query(BatchOperation).filter(
        BatchOperation.user_id == current_user.id
    ).order_by(
        BatchOperation.created_at.desc()
    ).limit(limit).all()

    return operations


@router.get("/batch-operations/{batch_id}", response_model=BatchOperationOut)
def get_batch_operation(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get details of a specific batch operation"""
    batch_op = db.query(BatchOperation).filter(
        BatchOperation.id == batch_id,
        BatchOperation.user_id == current_user.id
    ).first()

    if not batch_op:
        raise HTTPException(status_code=404, detail="Batch operation not found")

    return batch_op
