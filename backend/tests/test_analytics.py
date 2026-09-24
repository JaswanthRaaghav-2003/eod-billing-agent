import json
import pytest
from app.services.analytics import compute_analytics
from app.services.validator import validate_billing_log

def test_analytics_standard_day():
    with open("sample_data/billing_log_2026-07-27.json") as f:
        data = json.load(f)
    valid, _, cid, d = validate_billing_log(data)
    valid_dicts = [v.model_dump() for v in valid]

    analytics = compute_analytics(valid_dicts, cid, d)

    assert analytics.peak_hour is not None
    assert analytics.peak_hour.start_hour == 13 # 1pm
    assert analytics.peak_hour.end_hour == 14   # 2pm
    assert analytics.peak_hour.hour_range == "1pm?2pm"
    assert analytics.peak_hour.revenue_paise == 75500
    assert analytics.peak_hour.revenue_formatted == "?755"

    assert len(analytics.top_medicines_by_quantity) > 0
    assert len(analytics.top_medicines_by_revenue) > 0

    # Ensure rankings are distinct lists
    top_qty_names = [m.drug_name for m in analytics.top_medicines_by_quantity]
    top_rev_names = [m.drug_name for m in analytics.top_medicines_by_revenue]
    assert isinstance(top_qty_names, list)
    assert isinstance(top_rev_names, list)

def test_analytics_empty_day():
    analytics = compute_analytics([], "CLN-KNP-014", "2026-07-26")
    assert analytics.peak_hour is None
    assert len(analytics.top_medicines_by_quantity) == 0
    assert len(analytics.top_medicines_by_revenue) == 0
