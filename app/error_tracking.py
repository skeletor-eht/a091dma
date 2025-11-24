"""
Centralized error tracking and reporting.
"""
from typing import Optional, Dict, Any
from datetime import datetime
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .logging_config import get_logger

logger = get_logger(__name__)


class ErrorResponse:
    """Standard error response format."""

    @staticmethod
    def create(
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
        request_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a standardized error response.

        Args:
            error_code: Machine-readable error code
            message: Human-readable error message
            details: Additional error details
            request_id: Request ID for tracking

        Returns:
            Dictionary with error information
        """
        response = {
            "error": {
                "code": error_code,
                "message": message,
                "timestamp": datetime.utcnow().isoformat() + "Z",
            }
        }

        if details:
            response["error"]["details"] = details

        if request_id:
            response["error"]["request_id"] = request_id

        return response


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Handler for HTTP exceptions.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.warning(
        f"HTTP exception: {exc.status_code} - {exc.detail}",
        extra={
            "status_code": exc.status_code,
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
        }
    )

    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse.create(
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            request_id=request_id
        )
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handler for request validation errors.
    """
    request_id = getattr(request.state, "request_id", None)

    # Extract validation error details
    errors = []
    for error in exc.errors():
        errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })

    logger.warning(
        f"Validation error: {len(errors)} field(s) failed validation",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
            "validation_errors": errors,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse.create(
            error_code="VALIDATION_ERROR",
            message="Request validation failed",
            details={"fields": errors},
            request_id=request_id
        )
    )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Handler for unhandled exceptions.
    """
    request_id = getattr(request.state, "request_id", None)

    logger.exception(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "request_id": request_id,
            "exception_type": type(exc).__name__,
        }
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse.create(
            error_code="INTERNAL_SERVER_ERROR",
            message="An unexpected error occurred",
            details={"type": type(exc).__name__} if not isinstance(exc, Exception) else None,
            request_id=request_id
        )
    )
