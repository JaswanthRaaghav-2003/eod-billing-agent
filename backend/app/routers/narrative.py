from typing import Optional
from fastapi import APIRouter, HTTPException, Query, Body
from app.models.schemas import NarrativeReport, NarrativeGenerateRequest
from app.services.reconciliation import compute_reconciliation
from app.services.analytics import compute_analytics
from app.services.llm_agent import generate_eod_narrative
from app.database import db
from app.config import settings

router = APIRouter(prefix="/narrative", tags=["AI Narrative"])

@router.get("/{date_str}", response_model=NarrativeReport)
def get_eod_narrative(
    date_str: str,
    clinic_id: Optional[str] = Query(None),
    provider: str = Query("auto", description="LLM provider: 'auto', 'gemini', 'openai', or 'deterministic'"),
    recipient: Optional[str] = Query(None)
):
    """
    Generates the grounded WhatsApp summary for the day.
    Maps every figure back to ground truth in traced_figures.
    """
    visits = db.get_visits(clinic_id=clinic_id, date_str=date_str)
    cid = clinic_id or (visits[0]["clinic_id"] if visits else "CLN-KNP-014")

    reconciliation = compute_reconciliation(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )
    analytics = compute_analytics(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )

    narrative = generate_eod_narrative(
        reconciliation=reconciliation,
        analytics=analytics,
        provider=provider,
        recipient=recipient or settings.DEFAULT_DOCTOR_NAME
    )
    return narrative

@router.post("/generate", response_model=NarrativeReport)
def generate_custom_narrative(
    req: NarrativeGenerateRequest = Body(...)
):
    """
    POST endpoint to generate narrative with custom API key, recipient, or provider.
    """
    date_str = req.date or "2026-07-27"
    visits = db.get_visits(clinic_id=req.clinic_id, date_str=date_str)
    cid = req.clinic_id or (visits[0]["clinic_id"] if visits else "CLN-KNP-014")

    reconciliation = compute_reconciliation(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )
    analytics = compute_analytics(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )

    narrative = generate_eod_narrative(
        reconciliation=reconciliation,
        analytics=analytics,
        provider=req.provider or "auto",
        custom_api_key=req.api_key,
        recipient=req.custom_recipient or settings.DEFAULT_DOCTOR_NAME
    )
    return narrative
