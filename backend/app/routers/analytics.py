from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import AnalyticsReport
from app.services.analytics import compute_analytics
from app.database import db
from app.config import settings

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/{date_str}", response_model=AnalyticsReport)
def get_analytics(
    date_str: str,
    clinic_id: Optional[str] = Query(None, description="Optional clinic identifier filter")
):
    """
    Computes deterministic analytics for the specified date.
    Returns:
    - Revenue by hour-of-day (with peak hour identified)
    - Top medicines by quantity
    - Top medicines by revenue
    Purely deterministic ground truth.
    """
    visits = db.get_visits(clinic_id=clinic_id, date_str=date_str)
    cid = clinic_id or (visits[0]["clinic_id"] if visits else "CLN-KNP-014")

    report = compute_analytics(
        visits=visits,
        clinic_id=cid,
        date_str=date_str,
        clinic_name=settings.DEFAULT_CLINIC_NAME
    )
    return report
