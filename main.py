from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
import os

from app.db import Base, engine
from app.routers import auth as auth_router
from app.routers import clients as clients_router
from app.routers import rewrites as rewrites_router
from app.routers import admin as admin_router
from app.models import seed_demo_clients_and_admin  # ensures demo data
from app.config import settings
from app.logging_config import setup_logging, get_logger
from app.middleware import RequestLoggingMiddleware, ErrorHandlingMiddleware
from app.error_tracking import (
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from app import health as health_router

# Setup logging
setup_logging(
    log_level="INFO" if not settings.debug else "DEBUG",
    json_logs=not settings.debug,  # JSON logs in production, colored in dev
    log_file="app.log" if not settings.debug else None
)
logger = get_logger(__name__)

logger.info(f"Starting {settings.app_name} v{settings.app_version}")

# Create DB tables
Base.metadata.create_all(bind=engine)
seed_demo_clients_and_admin()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug
)

# Register exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Middleware - order matters! Applied in reverse order
# 1. CORS (applied last, runs first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Request logging (tracks all requests)
app.add_middleware(RequestLoggingMiddleware)

# 3. Error handling (catches unhandled exceptions)
app.add_middleware(ErrorHandlingMiddleware)

# Routers
app.include_router(health_router.router, tags=["health"])
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(clients_router.router, prefix="/clients", tags=["clients"])
app.include_router(rewrites_router.router, prefix="/rewrites", tags=["rewrites"])
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])


@app.get("/")
def read_root():
    """Serve the index.html file at the root path."""
    return FileResponse("index.html")


@app.get("/index.html")
def read_index():
    """Serve the index.html file."""
    return FileResponse("index.html")
