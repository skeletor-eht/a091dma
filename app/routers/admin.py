from typing import List
import io
import os

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from pypdf import PdfReader

from ..auth import get_password_hash
from ..db import SessionLocal
from ..deps import require_admin
from ..models import User, AuditEvent, TimeEntry, RewriteRecord, Client
from ..config import settings
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
# PDF Upload endpoints
# =========================


def validate_upload_file(file: UploadFile) -> None:
    """Validate uploaded file meets security requirements."""
    # Check if filename exists
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No filename provided"
        )

    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in settings.allowed_upload_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"File type {file_ext} not allowed. Allowed types: {', '.join(settings.allowed_upload_extensions)}"
        )

    # Check for potential path traversal
    if ".." in file.filename or "/" in file.filename or "\\" in file.filename:
        raise HTTPException(
            status_code=400,
            detail="Invalid filename. Filename cannot contain path separators."
        )


async def validate_file_size(file: UploadFile, max_size: int = None) -> bytes:
    """Read and validate file size."""
    if max_size is None:
        max_size = settings.max_upload_size

    # Read file content
    content = await file.read()

    # Check size
    if len(content) > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size: {max_size_mb:.1f}MB"
        )

    return content


def extract_text_from_pdf(file_content: bytes) -> str:
    """Extract text from a PDF file with enhanced error handling."""
    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Empty file provided"
        )

    try:
        pdf_reader = PdfReader(io.BytesIO(file_content))

        # Check if PDF is encrypted
        if pdf_reader.is_encrypted:
            raise HTTPException(
                status_code=400,
                detail="Encrypted PDFs are not supported"
            )

        # Extract text from all pages
        text_parts = []
        for page_num, page in enumerate(pdf_reader.pages, 1):
            try:
                text = page.extract_text()
                if text:
                    text_parts.append(text)
            except Exception as e:
                # Log warning but continue with other pages
                print(f"Warning: Failed to extract text from page {page_num}: {str(e)}")

        extracted_text = "\n\n".join(text_parts)

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="No text could be extracted from the PDF. The file may be scanned images or empty."
            )

        return extracted_text

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to process PDF: {str(e)}"
        )


@router.post("/clients/{client_id}/upload-guidelines")
async def upload_guidelines_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Upload a PDF and extract text for billing guidelines."""
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate file
    validate_upload_file(file)

    # Validate file size and read content
    content = await validate_file_size(file)

    # Extract text
    extracted_text = extract_text_from_pdf(content)

    # Update client
    client.billing_guidelines = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from {file.filename}",
        "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
    }


@router.post("/clients/{client_id}/upload-accepted-examples")
async def upload_accepted_examples_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Upload a PDF and extract text for accepted billing examples."""
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate file
    validate_upload_file(file)

    # Validate file size and read content
    content = await validate_file_size(file)

    # Extract text
    extracted_text = extract_text_from_pdf(content)

    # Update client
    client.accepted_examples = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from {file.filename}",
        "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
    }


@router.post("/clients/{client_id}/upload-denied-examples")
async def upload_denied_examples_pdf(
    client_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    """Upload a PDF and extract text for denied billing examples."""
    # Validate client exists
    client = db.query(Client).filter(Client.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    # Validate file
    validate_upload_file(file)

    # Validate file size and read content
    content = await validate_file_size(file)

    # Extract text
    extracted_text = extract_text_from_pdf(content)

    # Update client
    client.denied_examples = extracted_text
    db.commit()
    db.refresh(client)

    return {
        "status": "success",
        "message": f"Extracted {len(extracted_text)} characters from {file.filename}",
        "preview": extracted_text[:500] + "..." if len(extracted_text) > 500 else extracted_text
    }


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
