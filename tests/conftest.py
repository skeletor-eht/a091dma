"""
Pytest configuration and fixtures.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db import Base
from app.models import Client, User
from app.auth import get_password_hash


@pytest.fixture
def test_db():
    """
    Create a temporary in-memory database for testing.
    """
    # Create in-memory SQLite database
    engine = create_engine("sqlite:///:memory:")

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestSessionLocal = sessionmaker(bind=engine)
    db = TestSessionLocal()

    yield db

    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(test_db):
    """
    Create a test client in the database.
    """
    client = Client(
        id="TEST001",
        name="Test Client",
        code="TEST",
        billing_guidelines="Test guidelines",
        accepted_examples="Test accepted examples",
        denied_examples="Test denied examples"
    )
    test_db.add(client)
    test_db.commit()
    test_db.refresh(client)

    return client


@pytest.fixture
def test_user(test_db):
    """
    Create a test user in the database.
    """
    user = User(
        username="testuser",
        password_hash=get_password_hash("TestPass123"),
        role="user",
        is_active=True
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)

    return user


@pytest.fixture
def test_admin(test_db):
    """
    Create a test admin user in the database.
    """
    admin = User(
        username="testadmin",
        password_hash=get_password_hash("AdminPass123"),
        role="admin",
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)

    return admin
