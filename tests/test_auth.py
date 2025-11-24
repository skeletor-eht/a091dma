"""
Unit tests for authentication and password validation.
"""
import pytest
from fastapi import HTTPException

from app.auth import validate_password, get_password_hash, verify_password, create_access_token, decode_token


class TestPasswordValidation:
    """Test password validation rules."""

    def test_valid_password(self):
        """Test that valid passwords pass validation."""
        # Should not raise an exception
        validate_password("Admin123")
        validate_password("Demo1234")
        validate_password("SecureP@ss1")

    def test_password_too_short(self):
        """Test that passwords under 8 characters are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("Short1")
        assert exc_info.value.status_code == 400
        assert "at least 8 characters" in exc_info.value.detail.lower()

    def test_password_no_uppercase(self):
        """Test that passwords without uppercase letters are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("lowercase123")
        assert exc_info.value.status_code == 400
        assert "uppercase" in exc_info.value.detail.lower()

    def test_password_no_lowercase(self):
        """Test that passwords without lowercase letters are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("UPPERCASE123")
        assert exc_info.value.status_code == 400
        assert "lowercase" in exc_info.value.detail.lower()

    def test_password_no_digit(self):
        """Test that passwords without numbers are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_password("NoNumbers")
        assert exc_info.value.status_code == 400
        assert "number" in exc_info.value.detail.lower()


class TestPasswordHashing:
    """Test password hashing and verification."""

    def test_password_hash_generation(self):
        """Test that password hashing works."""
        password = "Admin123"
        hashed = get_password_hash(password)

        # Hash should be different from original
        assert hashed != password
        # Hash should be a string
        assert isinstance(hashed, str)
        # Hash should not be empty
        assert len(hashed) > 0

    def test_password_verification_success(self):
        """Test that correct passwords verify successfully."""
        password = "Admin123"
        hashed = get_password_hash(password)

        # Correct password should verify
        assert verify_password(password, hashed) is True

    def test_password_verification_failure(self):
        """Test that incorrect passwords fail verification."""
        password = "Admin123"
        hashed = get_password_hash(password)

        # Wrong password should not verify
        assert verify_password("WrongPass123", hashed) is False


class TestTokenOperations:
    """Test JWT token creation and decoding."""

    def test_token_creation(self):
        """Test that tokens are created successfully."""
        token = create_access_token(
            data={"sub": "admin", "role": "admin"}
        )

        # Token should be a non-empty string
        assert isinstance(token, str)
        assert len(token) > 0

    def test_token_decoding(self):
        """Test that tokens can be decoded successfully."""
        username = "testuser"
        role = "admin"

        token = create_access_token(
            data={"sub": username, "role": role}
        )

        decoded = decode_token(token)

        assert decoded.username == username
        assert decoded.role == role

    def test_token_with_different_roles(self):
        """Test tokens with different roles."""
        # Admin token
        admin_token = create_access_token(
            data={"sub": "admin", "role": "admin"}
        )
        admin_decoded = decode_token(admin_token)
        assert admin_decoded.role == "admin"

        # User token
        user_token = create_access_token(
            data={"sub": "user", "role": "user"}
        )
        user_decoded = decode_token(user_token)
        assert user_decoded.role == "user"
