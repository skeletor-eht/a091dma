from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI

from app.db import Base, engine
from app.routers import auth as auth_router
from app.routers import clients as clients_router
from app.routers import rewrites as rewrites_router
from app.routers import admin as admin_router
from app.models import seed_demo_clients_and_admin  # ensures demo data

# Create DB tables
Base.metadata.create_all(bind=engine)
seed_demo_clients_and_admin()

app = FastAPI(title="AI Time Entry Rewrite (Scaffolded)")

# CORS for your browser UI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router.router, prefix="/auth", tags=["auth"])
app.include_router(clients_router.router, prefix="/clients", tags=["clients"])
app.include_router(rewrites_router.router, prefix="/rewrites", tags=["rewrites"])
app.include_router(admin_router.router, prefix="/admin", tags=["admin"])

@app.get("/health")
def health():
    return {"status": "ok"}
