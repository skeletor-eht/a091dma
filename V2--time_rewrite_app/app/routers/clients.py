from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..db import SessionLocal
from ..models import Client
from ..schemas import ClientOut
from ..deps import get_current_user, get_user_permitted_clients

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ClientOut])
def list_clients(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    List clients that the current user has access to.
    Admins see all clients.
    Regular users only see their permitted clients.
    """
    # Get permitted client IDs for this user
    permitted_ids = get_user_permitted_clients(current_user, db)

    # Fetch only permitted clients
    return db.query(Client).filter(Client.id.in_(permitted_ids)).order_by(Client.name).all()
