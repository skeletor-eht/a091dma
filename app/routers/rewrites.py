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
