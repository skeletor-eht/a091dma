from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from ..auth import create_access_token, verify_password
from ..config import settings
from ..db import SessionLocal
from ..models import User
from ..schemas import Token

router = APIRouter()


def get_db():
    """Provide a DB session for this router."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class LoginPayload(BaseModel):
    username: str
    password: str


@router.post("/login", response_model=Token)
def login(payload: LoginPayload, db: Session = Depends(get_db)):
    """
    Login endpoint used by the SPA.

    Expects JSON body:
        { "username": "...", "password": "..." }

    Returns:
        {
          "access_token": "...",
          "token_type": "bearer",
          "username": "...",
          "role": "user" | "admin"
        }
    """
    user = (
        db.query(User)
        .filter(User.username == payload.username, User.is_active == True)
        .first()
    )
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(
        data={"sub": user.username, "role": user.role},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    return Token(access_token=access_token, username=user.username, role=user.role)
