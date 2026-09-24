from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ReconciliationReport
from app.services.reconciliation import compute_reconciliation
from app.database import db
from app.config import settings

router = APIRouter(prefix="/reconciliation", tags=["Reconciliation"])

@router.get("/{date_str}", response_model=ReconciliationReport)
def get_eod_reconciliation(
    date_str: str,
    clinic_id: Optional[str] = Query(None, description="Optional clinic identifier filter")
):
    """
    Computes deterministic EOD reconciliation for the specified date.
    Returns total billed, total collected, outstanding, and refunds split by payment mode.
    Purely deterministic ground truth.
    """
    visits = db.get_visits(clinic_id=clinic_id, date_str=date_str)
    
    # Resolve clinic name from DB or fallback
    cid = clinic_id or (visits[0]["clinic_id"] if visits else "CLN-KNP-014")
    
    report = compute_reconciliation(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )
    return report
