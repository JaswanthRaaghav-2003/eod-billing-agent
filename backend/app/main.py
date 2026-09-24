from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routers import ingestion, reconciliation, analytics, narrative
from app.database import db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: seed sample data if DB is empty
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

@app.get("/")
def root():
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

@app.get("/api/health")
def health_check():
    return {"status": "ok", "version": settings.VERSION}
