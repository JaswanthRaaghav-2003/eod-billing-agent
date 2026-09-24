from contextlib import asynccontextmanager
import os
from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Header, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from app.config import settings
from app.routers import ingestion, reconciliation, analytics, narrative
from app.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    existing = db.get_available_dates()
    if not existing:
        print("Initial database startup: seeding sample datasets...")
        ingestion.seed_sample_datasets()
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Deterministic EOD Billing Reconciliation, Analytics & Grounded Agentic Narrative API for SwasthiQ Kaagazy",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingestion.router, prefix=settings.API_PREFIX)
app.include_router(reconciliation.router, prefix=settings.API_PREFIX)
app.include_router(analytics.router, prefix=settings.API_PREFIX)
app.include_router(narrative.router, prefix=settings.API_PREFIX)

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}

def get_api_info():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "endpoints": {
            "ingestion": f"{settings.API_PREFIX}/ingest",
            "available_days": f"{settings.API_PREFIX}/ingest/days",
            "reconciliation": f"{settings.API_PREFIX}/reconciliation/{{date}}",
            "analytics": f"{settings.API_PREFIX}/analytics/{{date}}",
            "narrative": f"{settings.API_PREFIX}/narrative/{{date}}"
        }
    }

# Check for frontend dist directory
possible_dist_paths = [
    Path(__file__).resolve().parent.parent.parent / "frontend" / "dist",
    Path("frontend/dist"),
    Path("../frontend/dist")
]

dist_dir = None
for p in possible_dist_paths:
    if p.exists() and (p / "index.html").exists():
        dist_dir = p
        break

if dist_dir:
    assets_dir = dist_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/")
    def root(request: Request):
        accept = request.headers.get("accept", "")
        # If client explicitly wants HTML (like a browser), serve the frontend
        if "text/html" in accept and "application/json" not in accept:
            return FileResponse(str(dist_dir / "index.html"))
        return get_api_info()

    @app.get("/app/{full_path:path}")
    @app.get("/web/{full_path:path}")
    async def serve_spa_explicit(full_path: str):
        target = dist_dir / full_path
        if target.is_file():
            return FileResponse(str(target))
        return FileResponse(str(dist_dir / "index.html"))
else:
    @app.get("/")
    def root():
        return get_api_info()
