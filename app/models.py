from datetime import datetime
from sqlalchemy import (
    Column,
    String,
    Integer,
    DateTime,
    Float,
    Text,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship, Session

from .db import Base, SessionLocal


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")  # "user" or "admin"
    is_active = Column(Boolean, default=True)


class Client(Base):
    __tablename__ = "clients"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    code = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # New fields: where you paste guidelines + examples
    billing_guidelines = Column(Text, nullable=True)
    accepted_examples = Column(Text, nullable=True)
    denied_examples = Column(Text, nullable=True)

    time_entries = relationship("TimeEntry", back_populates="client")


class TimeEntry(Base):
    __tablename__ = "time_entries"

    id = Column(String, primary_key=True, index=True)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    original = Column(Text, nullable=False)
    hours = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    client = relationship("Client", back_populates="time_entries")
    rewrites = relationship("RewriteRecord", back_populates="time_entry")


class RewriteRecord(Base):
    __tablename__ = "rewrites"

    id = Column(String, primary_key=True, index=True)
    time_entry_id = Column(String, ForeignKey("time_entries.id"), nullable=False)
    standard = Column(Text, nullable=False)
    client_compliant = Column(Text, nullable=False)
    audit_safe = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    time_entry = relationship("TimeEntry", back_populates="rewrites")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    username = Column(String, nullable=False)
    role = Column(String, nullable=False)
    client_id = Column(String, ForeignKey("clients.id"), nullable=False)
    time_entry_id = Column(String, ForeignKey("time_entries.id"), nullable=False)
    rewrite_id = Column(String, ForeignKey("rewrites.id"), nullable=False)
    model_name = Column(String, nullable=False)
    rules_snapshot = Column(Text, nullable=False)


# Demo client rules – still here, but we’ll *augment* these with guidelines/examples
DEMO_RULES_BY_CLIENT_ID = {
    "C001": {
        "client_name": "Acme Manufacturing",
        "style": "formal litigation billing style",
        "forbidden_terms": ["email review", "miscellaneous"],
        "required_elements": [
            "Include subject of work",
            "Mention that correspondence was reviewed and analyzed",
        ],
        "guidance": "Use phrases like 'reviewed and analyzed client correspondence regarding <subject>'.",
    },
    "C002": {
        "client_name": "Globex Corporation",
        "style": "compliance-heavy, jurisdiction-aware",
        "forbidden_terms": ["internal admin", "general review"],
        "required_elements": [
            "Mention applicable jurisdiction if known",
            "Indicate whether task supports litigation hold or case strategy",
        ],
        "guidance": "Emphasize litigation hold, discovery planning, and jurisdictional context.",
    },
    "C003": {
        "client_name": "Initech LLC",
        "style": "plain-language, business-friendly",
        "forbidden_terms": [],
        "required_elements": [
            "Describe work in plain English suitable for a non-lawyer business stakeholder",
        ],
        "guidance": "Favor simple, direct descriptions over legal jargon.",
    },
}


def seed_demo_clients_and_admin():
    """
    Seed demo clients and users (admin/demo) if DB is empty.
    """
    db: Session = SessionLocal()
    try:
        # Seed clients
        if db.query(Client).count() == 0:
            demo_clients = [
                Client(
                    id="C001",
                    name="Acme Manufacturing",
                    code="ACME001",
                    billing_guidelines=None,
                    accepted_examples=None,
                    denied_examples=None,
                ),
                Client(
                    id="C002",
                    name="Globex Corporation",
                    code="GLOBEX01",
                    billing_guidelines=None,
                    accepted_examples=None,
                    denied_examples=None,
                ),
                Client(
                    id="C003",
                    name="Initech LLC",
                    code="INTECH99",
                    billing_guidelines=None,
                    accepted_examples=None,
                    denied_examples=None,
                ),
            ]
            db.add_all(demo_clients)
            db.commit()

        # Seed users: admin/admin123 and demo/demo123
        from .auth import get_password_hash

        if db.query(User).count() == 0:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("admin123"),
                role="admin",
                is_active=True,
            )
            demo_user = User(
                username="demo",
                password_hash=get_password_hash("demo123"),
                role="user",
                is_active=True,
            )
            db.add_all([admin_user, demo_user])
            db.commit()
    finally:
        db.close()
