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
