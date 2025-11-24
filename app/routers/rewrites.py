from datetime import datetime
from typing import List
import json

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..db import SessionLocal
from ..deps import get_current_user
from ..llm import call_ollama
from ..pagination import paginate, create_paginated_response, PaginatedResponse
from ..models import (
    Client,
    TimeEntry,
    RewriteRecord,
    AuditEvent,
    DEMO_RULES_BY_CLIENT_ID,
)
from ..schemas import (
    RewriteRequest,
    RewriteResponse,
    RewriteAndSaveRequest,
    SavedRewriteResponse,
    RewriteTagRequest,
    RewriteTagResponse,
)
from ..config import settings

router = APIRouter()


def get_db():
    """FastAPI dependency to provide a DB session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/rewrite", response_model=RewriteResponse)
async def rewrite(
    payload: RewriteRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Rewrite only (no persistence), using explicit rules from payload.
    """
    if not payload.original or not payload.original.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original narrative cannot be empty.",
        )

    rewrite = await call_ollama(
        original=payload.original,
        hours=payload.hours,
        rules=payload.rules,
    )
    return rewrite


@router.post("/rewrite-and-save", response_model=SavedRewriteResponse)
async def rewrite_and_save(
    payload: RewriteAndSaveRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Client-aware persistent rewrite that also logs an AuditEvent.

    Now includes:
    - Static demo rules (DEMO_RULES_BY_CLIENT_ID)
    - PLUS any billing_guidelines / accepted_examples / denied_examples
      configured for that client by an admin.
    """
    if not payload.original or not payload.original.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Original narrative cannot be empty.",
        )

    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found",
        )

    # Base rules from demo config
    base_rules = DEMO_RULES_BY_CLIENT_ID.get(payload.client_id, {}).copy()

    # Enrich rules with admin-provided guidelines and examples if present
    if client.billing_guidelines:
        base_rules["billing_guidelines"] = client.billing_guidelines
    if client.accepted_examples:
        base_rules["accepted_examples"] = client.accepted_examples
    if client.denied_examples:
        base_rules["denied_examples"] = client.denied_examples

    rewrite = await call_ollama(
        original=payload.original,
        hours=payload.hours,
        rules=base_rules,
    )

    now_ts = int(datetime.utcnow().timestamp() * 1000)
    time_entry_id = f"TE-{now_ts}"
    rewrite_id = f"RW-{now_ts}"
    audit_id = f"AE-{now_ts}"

    # TimeEntry
    te = TimeEntry(
        id=time_entry_id,
        client_id=client.id,
        original=payload.original,
        hours=payload.hours,
    )
    db.add(te)
    db.commit()
    db.refresh(te)

    # RewriteRecord
    rw = RewriteRecord(
        id=rewrite_id,
        time_entry_id=time_entry_id,
        standard=rewrite.standard,
        client_compliant=rewrite.client_compliant,
        audit_safe=rewrite.audit_safe,
        notes=rewrite.notes,
    )
    db.add(rw)
    db.commit()
    db.refresh(rw)

    # AuditEvent
    ae = AuditEvent(
        id=audit_id,
        timestamp=datetime.utcnow(),
        username=current_user.username,
        role=current_user.role,
        client_id=client.id,
        time_entry_id=time_entry_id,
        rewrite_id=rewrite_id,
        model_name=settings.model_name,
        rules_snapshot=json.dumps(base_rules),
    )
    db.add(ae)
    db.commit()

    return SavedRewriteResponse(
        time_entry_id=time_entry_id,
        rewrite_id=rewrite_id,
        client=client,
        rewrite=rewrite,
    )


@router.get("/recent", response_model=PaginatedResponse[SavedRewriteResponse])
def recent_time_entries(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    """
    Return the most recent saved time entries with their latest rewrite (paginated).

    Parameters:
    - page: Page number (1-indexed)
    - page_size: Number of items per page (max 100)
    """
    query = db.query(TimeEntry).order_by(TimeEntry.created_at.desc())

    # Paginate
    entries, total = paginate(query, page=page, page_size=page_size)

    results: List[SavedRewriteResponse] = []

    for te in entries:
        if not te.rewrites:
            continue

        latest_rw = sorted(
            te.rewrites, key=lambda r: r.created_at, reverse=True
        )[0]
        client = te.client

        results.append(
            SavedRewriteResponse(
                time_entry_id=te.id,
                rewrite_id=latest_rw.id,
                client=client,
                rewrite=RewriteResponse(
                    standard=latest_rw.standard,
                    client_compliant=latest_rw.client_compliant,
                    audit_safe=latest_rw.audit_safe,
                    notes=latest_rw.notes or "",
                ),
            )
        )

    return create_paginated_response(
        items=results,
        total=total,
        page=page,
        page_size=page_size
    )


@router.patch("/{rewrite_id}/tag", response_model=RewriteTagResponse)
async def tag_rewrite(
    rewrite_id: str,
    payload: RewriteTagRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Tag a rewrite with success/failure status and auto-ingest into client examples.
    """
    # Validate status
    valid_statuses = ["success", "failure", "not_submitted"]
    if payload.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}",
        )

    # Validate selected_variant if provided
    valid_variants = ["standard", "client_compliant", "audit_safe"]
    if payload.selected_variant and payload.selected_variant not in valid_variants:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid variant. Must be one of: {', '.join(valid_variants)}",
        )

    # Get the rewrite
    rewrite = db.query(RewriteRecord).filter(RewriteRecord.id == rewrite_id).first()
    if not rewrite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rewrite not found",
        )

    # Get the associated time entry and client
    time_entry = db.query(TimeEntry).filter(TimeEntry.id == rewrite.time_entry_id).first()
    if not time_entry:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated time entry not found",
        )

    client = db.query(Client).filter(Client.id == time_entry.client_id).first()
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Associated client not found",
        )

    # Update the rewrite with feedback
    rewrite.status = payload.status
    rewrite.selected_variant = payload.selected_variant
    rewrite.feedback_date = datetime.utcnow()
    rewrite.feedback_notes = payload.feedback_notes

    auto_ingested = False

    # Auto-ingest into client examples based on status
    if payload.status == "success" and payload.selected_variant:
        variant_text = getattr(rewrite, payload.selected_variant)
        example_entry = f"""
=== SUCCESS EXAMPLE (Auto-ingested {datetime.utcnow().strftime('%Y-%m-%d')}) ===
Original: {time_entry.original} ({time_entry.hours} hours)
Approved Rewrite: {variant_text}
Variant Used: {payload.selected_variant}
Notes: {payload.feedback_notes or 'None'}
---
"""
        if client.accepted_examples:
            client.accepted_examples += example_entry
        else:
            client.accepted_examples = example_entry
        auto_ingested = True

    elif payload.status == "failure" and payload.selected_variant:
        variant_text = getattr(rewrite, payload.selected_variant)
        example_entry = f"""
=== FAILURE EXAMPLE (Auto-ingested {datetime.utcnow().strftime('%Y-%m-%d')}) ===
Original: {time_entry.original} ({time_entry.hours} hours)
Rejected Rewrite: {variant_text}
Variant Used: {payload.selected_variant}
Reason: {payload.feedback_notes or 'Not specified'}
---
"""
        if client.denied_examples:
            client.denied_examples += example_entry
        else:
            client.denied_examples = example_entry
        auto_ingested = True

    # Commit all changes
    db.commit()
    db.refresh(rewrite)

    return RewriteTagResponse(
        rewrite_id=rewrite.id,
        status=rewrite.status,
        selected_variant=rewrite.selected_variant,
        feedback_date=rewrite.feedback_date,
        feedback_notes=rewrite.feedback_notes,
        auto_ingested=auto_ingested,
    )
