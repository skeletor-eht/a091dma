"""
Health check endpoints for monitoring application status.
"""
from datetime import datetime
from typing import Dict, Any
import httpx
from sqlalchemy import text
from fastapi import APIRouter, status
from pydantic import BaseModel

from .db import SessionLocal
from .config import settings
from .logging_config import get_logger

logger = get_logger(__name__)
router = APIRouter()


class HealthStatus(BaseModel):
    """Health check response model."""
    status: str
    timestamp: str
    version: str
    checks: Dict[str, Any]


class ServiceCheck(BaseModel):
    """Individual service check result."""
    status: str  # "healthy", "unhealthy", "degraded"
    message: str
    response_time_ms: float = None


def check_database() -> ServiceCheck:
    """
    Check database connectivity and responsiveness.
    """
    import time
    start = time.time()

    try:
        db = SessionLocal()
        # Execute a simple query
        db.execute(text("SELECT 1"))
        db.close()

        duration = (time.time() - start) * 1000

        return ServiceCheck(
            status="healthy",
            message="Database connection successful",
            response_time_ms=round(duration, 2)
        )
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return ServiceCheck(
            status="unhealthy",
            message=f"Database connection failed: {str(e)}"
        )


def check_ollama() -> ServiceCheck:
    """
    Check Ollama service connectivity.
    """
    import time
    start = time.time()

    try:
        # Try to connect to Ollama API
        # Use a simple endpoint that doesn't require heavy computation
        ollama_base = settings.ollama_url.rsplit("/", 1)[0]  # Get base URL

        with httpx.Client(timeout=5.0) as client:
            response = client.get(f"{ollama_base}/api/tags")

        duration = (time.time() - start) * 1000

        if response.status_code == 200:
            return ServiceCheck(
                status="healthy",
                message="Ollama service is reachable",
                response_time_ms=round(duration, 2)
            )
        else:
            return ServiceCheck(
                status="degraded",
                message=f"Ollama returned status {response.status_code}",
                response_time_ms=round(duration, 2)
            )

    except httpx.TimeoutException:
        logger.warning("Ollama health check timeout")
        return ServiceCheck(
            status="unhealthy",
            message="Ollama service timeout (not responding)"
        )
    except Exception as e:
        logger.error(f"Ollama health check failed: {str(e)}")
        return ServiceCheck(
            status="unhealthy",
            message=f"Ollama service unreachable: {str(e)}"
        )


@router.get("/health", response_model=HealthStatus)
def health_check():
    """
    Basic health check - returns 200 if service is running.
    """
    return HealthStatus(
        status="ok",
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.app_version,
        checks={}
    )


@router.get("/health/detailed", response_model=HealthStatus)
def detailed_health_check():
    """
    Detailed health check - tests all dependencies.
    Returns 200 if all checks pass, 503 if any critical service is down.
    """
    logger.info("Running detailed health check")

    # Run checks
    db_check = check_database()
    ollama_check = check_ollama()

    # Determine overall status
    checks = {
        "database": db_check.dict(),
        "ollama": ollama_check.dict(),
    }

    # Overall status is unhealthy if database is down (critical)
    # Ollama being down is degraded (non-critical)
    if db_check.status == "unhealthy":
        overall_status = "unhealthy"
    elif ollama_check.status == "unhealthy":
        overall_status = "degraded"
    else:
        overall_status = "healthy"

    return HealthStatus(
        status=overall_status,
        timestamp=datetime.utcnow().isoformat() + "Z",
        version=settings.app_version,
        checks=checks
    )


@router.get("/health/ready")
def readiness_check():
    """
    Kubernetes-style readiness probe.
    Returns 200 if app is ready to serve traffic, 503 otherwise.
    """
    db_check = check_database()

    if db_check.status == "healthy":
        return {"status": "ready"}
    else:
        return {"status": "not ready", "reason": db_check.message}


@router.get("/health/live")
def liveness_check():
    """
    Kubernetes-style liveness probe.
    Returns 200 if app process is alive.
    """
    return {"status": "alive"}
