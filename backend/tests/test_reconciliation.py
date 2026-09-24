import json
import pytest
from app.services.reconciliation import compute_reconciliation, format_inr
from app.services.validator import validate_billing_log

def test_format_inr():
    assert format_inr(0) == "?0"
    assert format_inr(60000) == "?600"
    assert format_inr(4285000) == "?42,850"
    assert format_inr(123456700) == "?12,34,567"
    assert format_inr(-24000) == "-?240"
    assert format_inr(51550) == "?515.50"

def test_non_happy_path_refunds_only_day():
    """Covers non-happy-path day: 2026-07-25 with 3 refund visits."""
    with open("sample_data/billing_log_2026-07-25.json") as f:
        data = json.load(f)
    valid, errs, cid, d = validate_billing_log(data)
    assert len(valid) == 3
    assert len(errs) == 0

    valid_dicts = [v.model_dump() for v in valid]
    report = compute_reconciliation(valid_dicts, cid, d)

    assert report.total_visits == 0 # 0 regular sales visits
    assert report.refund_visits == 3 # 3 refunds
    assert report.total_billed_paise == 0
    assert report.total_collected_paise == 0
    assert report.total_outstanding_paise == 0
    # 24000 + 22000 + 3000 = 49000 paise
    assert report.total_refunds_paise == 49000
    assert report.total_refunds_formatted == "?490"
    assert report.collection_percentage == 0.0

def test_non_happy_path_empty_day():
    """Covers non-happy-path day: 2026-07-26 with 0 visits (empty array)."""
    with open("sample_data/billing_log_2026-07-26.json") as f:
        data = json.load(f)
    valid, errs, cid, d = validate_billing_log(data)
    assert len(valid) == 0

    report = compute_reconciliation([], "CLN-KNP-014", "2026-07-26")
    assert report.total_visits == 0
    assert report.refund_visits == 0
    assert report.total_billed_paise == 0
    assert report.total_collected_paise == 0
    assert report.total_outstanding_paise == 0
    assert report.total_refunds_paise == 0
    assert report.collection_percentage == 0.0

def test_happy_path_standard_day():
    """Covers 2026-07-27: 18 valid visits, 1 malformed rejected row."""
    with open("sample_data/billing_log_2026-07-27.json") as f:
        data = json.load(f)
    valid, errs, cid, d = validate_billing_log(data)
    assert len(valid) == 18
    assert len(errs) == 1

    valid_dicts = [v.model_dump() for v in valid]
    report = compute_reconciliation(valid_dicts, cid, d)

    assert report.total_visits == 18
    assert report.refund_visits == 0
    assert report.total_billed_paise == 319000
    assert report.total_collected_paise == 317200
    assert report.total_outstanding_paise == 1800
    assert report.pending_invoices_count == 3
    assert len(report.payment_mode_breakdown) == 3
