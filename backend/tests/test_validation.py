import pytest
from app.services.validator import validate_visit_record, validate_billing_log
from app.models.schemas import PaymentMode

def test_valid_visit_record():
    record = {
        "clinic_id": "CLN-KNP-014",
        "visit_id": "V-20260727-001",
        "timestamp": "2026-07-27T09:10:00Z",
        "doctor_id": "DOC-014-01",
        "line_items": [
            {"drug_name": "PARACETAMOL", "qty": 3, "unit_price_paise": 2000}
        ],
        "payment_mode": "cash",
        "amount_paid_paise": 6000,
        "discount_paise": 0,
        "is_refund": False
    }
    rec, errs = validate_visit_record(record, row_idx=1)
    assert rec is not None
    assert len(errs) == 0
    assert rec.payment_mode == PaymentMode.CASH
    assert rec.amount_paid_paise == 6000

def test_malformed_missing_payment_mode():
    # Like visit 19 in sample dataset
    record = {
        "clinic_id": "CLN-KNP-014",
        "visit_id": "V-20260727-019",
        "timestamp": "2026-07-27T17:40:00Z",
        "doctor_id": "DOC-014-01",
        "line_items": [
            {"drug_name": "OMEPRAZOLE", "qty": 1, "unit_price_paise": 4000}
        ],
        "amount_paid_paise": 4000,
        "discount_paise": 0,
        "is_refund": False
    }
    rec, errs = validate_visit_record(record, row_idx=19)
    assert rec is None
    assert len(errs) == 1
    assert errs[0].field == "payment_mode"
    assert "Missing required field 'payment_mode'" in errs[0].error
    assert "cash" in errs[0].actionable_guidance

def test_invalid_refund_positive_amount():
    record = {
        "clinic_id": "CLN-KNP-014",
        "visit_id": "V-TEST-REFUND",
        "timestamp": "2026-07-25T10:00:00Z",
        "line_items": [{"drug_name": "ATORVASTATIN", "qty": 1, "unit_price_paise": 12000}],
        "payment_mode": "card",
        "amount_paid_paise": 12000, # Positive on a refund is invalid
        "is_refund": True
    }
    rec, errs = validate_visit_record(record, row_idx=1)
    assert rec is None
    assert any("amount_paid_paise" in e.field for e in errs)

def test_invalid_qty_zero_or_negative():
    record = {
        "clinic_id": "CLN-KNP-014",
        "visit_id": "V-TEST-QTY",
        "timestamp": "2026-07-27T10:00:00Z",
        "line_items": [{"drug_name": "AMOXICILLIN", "qty": 0, "unit_price_paise": 6000}],
        "payment_mode": "upi",
        "amount_paid_paise": 0,
        "is_refund": False
    }
    rec, errs = validate_visit_record(record, row_idx=1)
    assert rec is None
    assert any("qty" in e.field for e in errs)

def test_validate_billing_log_empty():
    records = []
    valid, errs, cid, d = validate_billing_log(records)
    assert len(valid) == 0
    assert len(errs) == 0
