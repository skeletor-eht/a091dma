from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..db import SessionLocal
from ..models import Client
from ..schemas import ClientOut

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[ClientOut])
def list_clients(db: Session = Depends(get_db)):
    return db.query(Client).order_by(Client.name).all()
