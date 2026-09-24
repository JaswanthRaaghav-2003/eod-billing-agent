import json
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import db

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "endpoints" in data

def test_seed_sample_data():
    response = client.post("/api/ingest/seed-sample-data")
    assert response.status_code == 200
    data = response.json()
    assert "datasets" in data

def test_get_available_days():
    response = client.get("/api/ingest/days")
    assert response.status_code == 200
    days = response.json()
    assert isinstance(days, list)
    assert any(d["date"] == "2026-07-27" for d in days)

def test_get_reconciliation_endpoint():
    response = client.get("/api/reconciliation/2026-07-27")
    assert response.status_code == 200
    rep = response.json()
    assert rep["clinic_id"] == "CLN-KNP-014"
    assert rep["total_visits"] == 18
    assert len(rep["payment_mode_breakdown"]) == 3

def test_get_analytics_endpoint():
    response = client.get("/api/analytics/2026-07-27")
    assert response.status_code == 200
    data = response.json()
    assert data["peak_hour"]["hour_range"] == "1pm?2pm"
    assert len(data["top_medicines_by_quantity"]) > 0
    assert len(data["top_medicines_by_revenue"]) > 0

def test_get_narrative_endpoint():
    response = client.get("/api/narrative/2026-07-27")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert len(data["traced_figures"]) > 0

def test_strict_ingestion_rejection():
    # Attempting to ingest a malformed row in strict mode returns HTTP 422
    malformed_row = [
        {
            "clinic_id": "CLN-KNP-014",
            "visit_id": "V-MALFORMED-1",
            "timestamp": "2026-07-27T10:00:00Z",
            # missing payment_mode
            "line_items": [{"drug_name": "PARACETAMOL", "qty": 1, "unit_price_paise": 1000}],
            "amount_paid_paise": 1000,
            "is_refund": False
        }
    ]
    resp = client.post("/api/ingest?strict=true", json=malformed_row)
    assert resp.status_code == 422
    err_body = resp.json()
    assert "malformed row(s) found" in err_body["detail"]["message"]
