from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..auth import get_password_hash
from ..db import SessionLocal
from ..deps import require_admin
from ..models import User, AuditEvent, TimeEntry, RewriteRecord, Client
from ..schemas import (
    UserCreate,
    UserOut,
    AuditEntryOut,
    ClientOut,
    RewriteResponse,
    ClientAdminCreate,
    ClientAdminUpdate,
    ClientAdminDetail,
)

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# User management (existing)
# =========================


@router.post("/users", response_model=UserOut)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    existing = db.query(User).filter(User.username == payload.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Username already exists"
        )

    user = User(
        username=payload.username,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    return db.query(User).order_by(User.username).all()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete built-in admin user")

    db.delete(user)
    db.commit()
    return {"status": "deleted"}


# =========================
# Admin client management
# =========================


@router.get("/clients", response_model=List[ClientAdminDetail])
def admin_list_clients(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    clients = db.query(Client).order_by(Client.name).all()
    return clients


@router.post("/clients", response_model=ClientAdminDetail)
def admin_create_client(
    payload: ClientAdminCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    existing = db.query(Client).filter(Client.id == payload.id).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID already exists",
        )

    client = Client(
        id=payload.id,
        name=payload.name,
        code=payload.code,
        billing_guidelines=payload.billing_guidelines,
        accepted_examples=payload.accepted_examples,
        denied_examples=payload.denied_examples,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client


@router.put("/clients/{client_id}", response_model=ClientAdminDetail)
def admin_update_client(
    client_id: str,
    payload: ClientAdminUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    client.name = payload.name
    client.code = payload.code
    client.billing_guidelines = payload.billing_guidelines
    client.accepted_examples = payload.accepted_examples
    client.denied_examples = payload.denied_examples

    db.commit()
    db.refresh(client)
    return client


@router.delete("/clients/{client_id}")
def admin_delete_client(
    client_id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Optional: prevent deleting demo C001–C003 if you want
    # if client_id in ("C001", "C002", "C003"):
    #     raise HTTPException(status_code=400, detail="Cannot delete demo clients")

    db.delete(client)
    db.commit()
    return {"status": "deleted"}


# =========================
# Audit trail (existing)
# =========================


@router.get("/audit-events", response_model=List[AuditEntryOut])
def audit_events(
    limit: int = 50,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    events = (
        db.query(AuditEvent)
        .order_by(AuditEvent.timestamp.desc())
        .limit(limit)
        .all()
    )

    results: list[AuditEntryOut] = []
    for ev in events:
        te = db.query(TimeEntry).filter(TimeEntry.id == ev.time_entry_id).first()
        rw = db.query(RewriteRecord).filter(RewriteRecord.id == ev.rewrite_id).first()
        client = db.query(Client).filter(Client.id == ev.client_id).first()
        if not te or not rw or not client:
            continue

        results.append(
            AuditEntryOut(
                id=ev.id,
                timestamp=ev.timestamp,
                username=ev.username,
                role=ev.role,
                client=ClientOut.model_validate(client),
                time_entry_id=te.id,
                rewrite_id=rw.id,
                original=te.original,
                standard=rw.standard,
                client_compliant=rw.client_compliant,
                audit_safe=rw.audit_safe,
                notes=rw.notes or "",
            )
        )

    return results
