"""
Unit tests for input validation and sanitization.
"""
import pytest
from fastapi import HTTPException

from app.validators import validate_client_id, sanitize_text_input


class TestClientIDValidation:
    """Test client ID validation."""

    def test_valid_client_ids(self):
        """Test that valid client IDs pass validation."""
        assert validate_client_id("C001") == "C001"
        assert validate_client_id("CLIENT-123") == "CLIENT-123"
        assert validate_client_id("Test_Client_1") == "Test_Client_1"

    def test_empty_client_id(self):
        """Test that empty client IDs are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_client_id("")
        assert exc_info.value.status_code == 400
        assert "cannot be empty" in exc_info.value.detail.lower()

    def test_whitespace_only_client_id(self):
        """Test that whitespace-only client IDs are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_client_id("   ")
        assert exc_info.value.status_code == 400

    def test_invalid_characters(self):
        """Test that client IDs with invalid characters are rejected."""
        with pytest.raises(HTTPException) as exc_info:
            validate_client_id("client@123")
        assert exc_info.value.status_code == 400
        assert "letters, numbers, hyphens" in exc_info.value.detail.lower()

    def test_client_id_too_long(self):
        """Test that client IDs over 50 characters are rejected."""
        long_id = "A" * 51
        with pytest.raises(HTTPException) as exc_info:
            validate_client_id(long_id)
        assert exc_info.value.status_code == 400
        assert "50 characters or less" in exc_info.value.detail.lower()

    def test_client_id_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        assert validate_client_id("  C001  ") == "C001"


class TestTextSanitization:
    """Test text input sanitization."""

    def test_normal_text(self):
        """Test that normal text passes through unchanged."""
        text = "This is normal text."
        assert sanitize_text_input(text) == text

    def test_whitespace_trimming(self):
        """Test that leading/trailing whitespace is trimmed."""
        assert sanitize_text_input("  text  ") == "text"

    def test_null_byte_removal(self):
        """Test that null bytes are removed."""
        text_with_nulls = "text\x00with\x00nulls"
        result = sanitize_text_input(text_with_nulls)
        assert "\x00" not in result
        assert result == "textwithnulls"

    def test_text_too_long(self):
        """Test that text over max length is rejected."""
        long_text = "A" * 10001
        with pytest.raises(HTTPException) as exc_info:
            sanitize_text_input(long_text, max_length=10000)
        assert exc_info.value.status_code == 400
        assert "too long" in exc_info.value.detail.lower()

    def test_none_input(self):
        """Test that None input returns empty string."""
        assert sanitize_text_input(None) == ""

    def test_multiline_text(self):
        """Test that multiline text is preserved."""
        multiline = "Line 1\nLine 2\nLine 3"
        assert sanitize_text_input(multiline) == multiline
