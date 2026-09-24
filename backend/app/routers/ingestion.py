import json
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, UploadFile, File, Body
from app.models.schemas import IngestionResult, ValidationErrorDetail
from app.services.validator import validate_billing_log
from app.database import db
from app.config import settings
from pathlib import Path

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

@router.post("", response_model=IngestionResult)
async def ingest_billing_log(
    records: List[Dict[str, Any]] = Body(...),
    strict: bool = Query(False, description="If true, rejects entire file if any row is malformed"),
    clinic_name: Optional[str] = Query(None, description="Optional custom clinic name")
):
    """
    Ingests and validates a clinic billing log.
    Rejects malformed rows with specific, actionable errors.
    If strict=True, fails with 422 if any row is malformed.
    If strict=False, records valid rows and logs actionable error reports for malformed rows.
    """
    if not isinstance(records, list):
        raise HTTPException(
            status_code=400,
            detail={"error": "Payload must be a JSON array of billing visit records."}
        )

    valid_records, errors, detected_clinic_id, detected_date = validate_billing_log(records)

    total_rows = len(records)
    valid_count = len(valid_records)
    malformed_count = len(errors)

    if strict and malformed_count > 0:
        raise HTTPException(
            status_code=422,
            detail={
                "message": f"Log rejected: {malformed_count} malformed row(s) found.",
                "total_rows": total_rows,
                "malformed_rows_count": malformed_count,
                "validation_errors": [e.model_dump() for e in errors]
            }
        )

    clinic_id = detected_clinic_id or "CLN-KNP-014"
    date_str = detected_date or "2026-07-27"
    resolved_name = clinic_name or settings.DEFAULT_CLINIC_NAME

    # Convert valid pydantic records to dicts for DB
    valid_dicts = [r.model_dump() for r in valid_records]

    # Save to SQLite atomically
    db.save_visits_atomically(
        clinic_id=clinic_id,
        clinic_name=resolved_name,
        date_str=date_str,
        valid_visits=valid_dicts,
        total_rows=total_rows,
        malformed_count=malformed_count,
        errors=[e.model_dump() for e in errors]
    )

    status_str = "success" if malformed_count == 0 else "partial_success"
    msg = f"Processed {valid_count} valid visit(s)."
    if malformed_count > 0:
        msg += f" {malformed_count} malformed row(s) rejected with actionable errors."

    return IngestionResult(
        status=status_str,
        message=msg,
        date=date_str,
        clinic_id=clinic_id,
        total_rows=total_rows,
        valid_rows_count=valid_count,
        malformed_rows_count=malformed_count,
        validation_errors=errors
    )

@router.post("/file", response_model=IngestionResult)
async def ingest_billing_file(
    file: UploadFile = File(...),
    strict: bool = Query(False),
    clinic_name: Optional[str] = Query(None)
):
    """Upload and ingest a JSON file directly."""
    try:
        content = await file.read()
        records = json.loads(content.decode("utf-8"))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail={"error": f"Invalid JSON file: {str(e)}"}
        )

    return await ingest_billing_log(records=records, strict=strict, clinic_name=clinic_name)

@router.get("/days")
def list_available_days():
    """Returns all dates present in the system with summary counts."""
    return db.get_available_dates()

@router.post("/seed-sample-data")
def seed_sample_datasets():
    """Seeds the 3 provided sample clinic days from sample_data folder."""
    results = {}
    base_dir = Path("d:/Swasthiq/sample_data")
    if not base_dir.exists():
        base_dir = Path("sample_data")

    sample_files = [
        "billing_log_2026-07-27.json",
        "billing_log_2026-07-25.json",
        "billing_log_2026-07-26.json"
    ]

    for fname in sample_files:
        fpath = base_dir / fname
        if fpath.exists():
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                valid_records, errors, cid, d = validate_billing_log(data)

                # Determine fallback date from filename if file was empty
                if not d:
                    # extract date from filename
                    parts = fname.replace("billing_log_", "").replace(".json", "")
                    d = parts
                if not cid:
                    cid = "CLN-KNP-014"

                valid_dicts = [r.model_dump() for r in valid_records]
                db.save_visits_atomically(
                    clinic_id=cid,
                    clinic_name=settings.DEFAULT_CLINIC_NAME,
                    date_str=d,
                    valid_visits=valid_dicts,
                    total_rows=len(data),
                    malformed_count=len(errors),
                    errors=[e.model_dump() for e in errors]
                )
                results[fname] = {
                    "status": "seeded",
                    "date": d,
                    "valid_rows": len(valid_records),
                    "malformed_rows": len(errors)
                }
            except Exception as e:
                results[fname] = {"status": "error", "error": str(e)}

    return {"message": "Sample datasets seeded successfully", "datasets": results}
