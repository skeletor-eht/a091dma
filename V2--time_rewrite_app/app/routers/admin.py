from typing import List
from io import BytesIO

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pypdf import PdfReader

from ..auth import get_password_hash
from ..db import SessionLocal
from ..deps import require_admin
from ..models import User, AuditEvent, TimeEntry, RewriteRecord, Client, UserClientPermission
from ..schemas import (
    UserCreate,
    UserOut,
    UserWithPermissions,
    UserUpdate,
    PasswordReset,
    UserClientPermissionCreate,
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


# =========================
# PDF Upload endpoints
# =========================


def extract_text_from_pdf(pdf_file: bytes) -> str:
    """
    Extract text from PDF bytes.
    """
    try:
        pdf_reader = PdfReader(BytesIO(pdf_file))
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text.strip()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to extract text from PDF: {str(e)}"
        )


@router.post("/clients/{client_id}/upload-guidelines-pdf")
async def upload_guidelines_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Upload and extract text from client billing guidelines PDF.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    pdf_bytes = await file.read()
    extracted_text = extract_text_from_pdf(pdf_bytes)

    client.guidelines_pdf_text = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from guidelines PDF",
        "preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
    }


@router.post("/clients/{client_id}/upload-successful-examples-pdf")
async def upload_successful_examples_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Upload and extract text from successful billing examples PDF.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    pdf_bytes = await file.read()
    extracted_text = extract_text_from_pdf(pdf_bytes)

    client.successful_examples_pdf_text = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from successful examples PDF",
        "preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
    }


@router.post("/clients/{client_id}/upload-failed-examples-pdf")
async def upload_failed_examples_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Upload and extract text from failed billing examples PDF.
    """
    if not file.filename.endswith('.pdf'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )

    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    pdf_bytes = await file.read()
    extracted_text = extract_text_from_pdf(pdf_bytes)

    client.failed_examples_pdf_text = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from failed examples PDF",
        "preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text
    }


# =========================
# User Management endpoints
# =========================


@router.get("/users-with-permissions", response_model=List[UserWithPermissions])
def list_users_with_permissions(
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    List all users with their client permissions.
    """
    users = db.query(User).order_by(User.username).all()

    result = []
    for user in users:
        # Get permitted client IDs for this user
        permitted_ids = [perm.client_id for perm in user.client_permissions]

        result.append(UserWithPermissions(
            id=user.id,
            username=user.username,
            role=user.role,
            is_active=user.is_active,
            permitted_client_ids=permitted_ids,
        ))

    return result


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Update user details (username, role, is_active).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Prevent deactivating or changing admin user
    if user.username == "admin":
        if payload.role and payload.role != "admin":
            raise HTTPException(status_code=400, detail="Cannot change admin role")
        if payload.is_active == False:
            raise HTTPException(status_code=400, detail="Cannot deactivate admin user")

    # Update fields
    if payload.username:
        # Check if username is already taken
        existing = db.query(User).filter(
            User.username == payload.username,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(status_code=400, detail="Username already exists")
        user.username = payload.username

    if payload.role:
        user.role = payload.role

    if payload.is_active is not None:
        user.is_active = payload.is_active

    db.commit()
    db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password")
def reset_user_password(
    user_id: int,
    payload: PasswordReset,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Reset a user's password (admin only).
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if len(payload.new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    user.password_hash = get_password_hash(payload.new_password)
    db.commit()

    return {"status": "success", "message": f"Password reset for user {user.username}"}


@router.delete("/users/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Delete a user (admin only).
    Prevents deletion of built-in admin user.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.username == "admin":
        raise HTTPException(status_code=400, detail="Cannot delete built-in admin user")

    db.delete(user)
    db.commit()
    return {"status": "deleted", "message": f"User {user.username} deleted"}


# =========================
# User-Client Permission Management
# =========================


@router.post("/user-permissions")
def assign_client_permission(
    payload: UserClientPermissionCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Assign a client to a user (grant permission).
    """
    # Check user exists
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check client exists
    client = db.query(Client).filter(Client.id == payload.client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Check if permission already exists
    existing = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == payload.user_id,
        UserClientPermission.client_id == payload.client_id
    ).first()

    if existing:
        return {"status": "already_exists", "message": "Permission already granted"}

    # Create permission
    perm = UserClientPermission(
        user_id=payload.user_id,
        client_id=payload.client_id
    )
    db.add(perm)
    db.commit()

    return {
        "status": "success",
        "message": f"Granted {user.username} access to {client.name}"
    }


@router.delete("/user-permissions/{user_id}/{client_id}")
def revoke_client_permission(
    user_id: int,
    client_id: str,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Revoke a user's access to a client.
    """
    perm = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == user_id,
        UserClientPermission.client_id == client_id
    ).first()

    if not perm:
        raise HTTPException(status_code=404, detail="Permission not found")

    db.delete(perm)
    db.commit()

    return {"status": "revoked", "message": "Client access revoked"}


@router.post("/user-permissions/{user_id}/set-all")
def set_user_permissions(
    user_id: int,
    client_ids: List[str],
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """
    Set all client permissions for a user at once.
    Replaces existing permissions.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Delete existing permissions
    db.query(UserClientPermission).filter(
        UserClientPermission.user_id == user_id
    ).delete()

    # Add new permissions
    for client_id in client_ids:
        # Verify client exists
        client = db.query(Client).filter(Client.id == client_id).first()
        if client:
            perm = UserClientPermission(user_id=user_id, client_id=client_id)
            db.add(perm)

    db.commit()

    return {
        "status": "success",
        "message": f"Set {len(client_ids)} client permissions for {user.username}"
    }
