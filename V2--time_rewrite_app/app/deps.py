from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from .db import SessionLocal
from .auth import decode_token
from .models import User, UserClientPermission
from .schemas import TokenData


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(request: Request, db: Session = Depends(get_db)) -> User:
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing or invalid token")

    token = auth.split()[1]
    try:
        token_data: TokenData = decode_token(token)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.username == token_data.username, User.is_active == True).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    if current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


def check_client_access(user: User, client_id: str, db: Session) -> bool:
    """
    Check if a user has access to a specific client.
    Admins have access to all clients.
    Regular users must have explicit permission.
    """
    # Admins have access to everything
    if user.role == "admin":
        return True

    # Check if user has permission for this client
    permission = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == user.id,
        UserClientPermission.client_id == client_id
    ).first()

    return permission is not None


def get_user_permitted_clients(user: User, db: Session) -> list[str]:
    """
    Get list of client IDs this user can access.
    Admins get all clients.
    Regular users get only their permitted clients.
    """
    if user.role == "admin":
        # Return all client IDs
        from .models import Client
        return [c.id for c in db.query(Client).all()]

    # Return permitted client IDs
    permissions = db.query(UserClientPermission).filter(
        UserClientPermission.user_id == user.id
    ).all()

    return [perm.client_id for perm in permissions]
