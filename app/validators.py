"""Input validation and sanitization utilities."""
import re
from fastapi import HTTPException, status


def validate_client_id(client_id: str) -> str:
    """
    Validate and sanitize client ID.
    Only allow alphanumeric characters and hyphens.
    """
    if not client_id or not client_id.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID cannot be empty"
        )

    client_id = client_id.strip()

    # Only allow alphanumeric and hyphens
    if not re.match(r"^[A-Za-z0-9\-_]+$", client_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID can only contain letters, numbers, hyphens, and underscores"
        )

    if len(client_id) > 50:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Client ID must be 50 characters or less"
        )

    return client_id


def validate_username(username: str) -> str:
    """
    Validate and sanitize username.
    Only allow alphanumeric characters, underscores, and hyphens.
    """
    if not username or not username.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username cannot be empty"
        )

    username = username.strip().lower()

    # Only allow alphanumeric, underscore, and hyphen
    if not re.match(r"^[a-z0-9_\-]+$", username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username can only contain lowercase letters, numbers, underscores, and hyphens"
        )

    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be at least 3 characters long"
        )

    if len(username) > 30:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must be 30 characters or less"
        )

    return username


def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize general text input.
    Remove null bytes and enforce length limits.
    """
    if text is None:
        return ""

    # Remove null bytes
    text = text.replace("\x00", "")

    # Enforce length limit
    if len(text) > max_length:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Text input too long. Maximum {max_length} characters allowed."
        )

    return text.strip()


def validate_hours(hours: float) -> float:
    """Validate hours input for time entries."""
    if hours < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours cannot be negative"
        )

    if hours > 24:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Hours cannot exceed 24 in a single entry"
        )

    # Round to 2 decimal places
    return round(hours, 2)
