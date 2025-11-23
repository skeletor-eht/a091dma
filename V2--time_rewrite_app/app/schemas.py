from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel


# --------- Auth / Users ---------


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str


class TokenData(BaseModel):
    username: str
    role: str


class UserBase(BaseModel):
    username: str
    role: str


class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "user"


class UserOut(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True


class UserWithPermissions(UserOut):
    """User with list of permitted client IDs."""
    permitted_client_ids: List[str] = []


class UserUpdate(BaseModel):
    """Update user details (admin only)."""
    username: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class PasswordReset(BaseModel):
    """Reset user password (admin only)."""
    new_password: str


class UserClientPermissionCreate(BaseModel):
    """Assign client permission to user."""
    user_id: int
    client_id: str


# --------- Clients ---------


class ClientOut(BaseModel):
    id: str
    name: str
    code: Optional[str] = None

    class Config:
        from_attributes = True


class ClientAdminBase(BaseModel):
    name: str
    code: Optional[str] = None
    billing_guidelines: Optional[str] = None
    accepted_examples: Optional[str] = None
    denied_examples: Optional[str] = None


class ClientAdminCreate(ClientAdminBase):
    # For now admin provides string IDs like "C004"
    id: str


class ClientAdminUpdate(ClientAdminBase):
    pass


class ClientAdminDetail(ClientOut):
    billing_guidelines: Optional[str] = None
    accepted_examples: Optional[str] = None
    denied_examples: Optional[str] = None
    guidelines_pdf_text: Optional[str] = None
    successful_examples_pdf_text: Optional[str] = None
    failed_examples_pdf_text: Optional[str] = None


# --------- Rewrite + Audit ---------


class RewriteRequest(BaseModel):
    original: str
    hours: float
    rules: Optional[dict] = None


class RewriteResponse(BaseModel):
    standard: str
    client_compliant: str
    audit_safe: str
    notes: str


class RewriteAndSaveRequest(BaseModel):
    client_id: str
    original: str
    hours: float


class SavedRewriteResponse(BaseModel):
    time_entry_id: str
    rewrite_id: str
    client: ClientOut
    rewrite: RewriteResponse


class AuditEntryOut(BaseModel):
    id: str
    timestamp: datetime
    username: str
    role: str
    client: ClientOut
    time_entry_id: str
    rewrite_id: str
    original: str
    standard: str
    client_compliant: str
    audit_safe: str
    notes: str


# --------- Bulk Operations ---------


class BatchOperationOut(BaseModel):
    id: str
    operation_type: str
    filename: str
    total_rows: int
    successful_rows: int
    failed_rows: int
    status: str
    error_log: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class CSVImportRow(BaseModel):
    """Single row from CSV import"""
    client_id: str
    original: str
    hours: float


# --------- History ---------


class RewriteVersionOut(BaseModel):
    id: str
    version_number: int
    standard: str
    client_compliant: str
    audit_safe: str
    notes: Optional[str] = None
    created_by: str
    created_at: datetime
    is_current: bool

    class Config:
        from_attributes = True


# --------- Templates ---------


class TemplateCreate(BaseModel):
    client_id: Optional[str] = None
    name: str
    template_type: str  # "phrase" or "full_rewrite"
    original_text: Optional[str] = None
    rewrite_text: str
    category: Optional[str] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    rewrite_text: Optional[str] = None
    category: Optional[str] = None


class TemplateOut(BaseModel):
    id: str
    user_id: int
    client_id: Optional[str] = None
    name: str
    template_type: str
    original_text: Optional[str] = None
    rewrite_text: str
    category: Optional[str] = None
    usage_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
