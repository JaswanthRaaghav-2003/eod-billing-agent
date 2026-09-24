import json
import pytest
from app.services.reconciliation import compute_reconciliation
from app.services.analytics import compute_analytics
from app.services.llm_agent import generate_eod_narrative, generate_deterministic_grounded_summary
from app.services.grounding_verifier import verify_and_trace_narrative
from app.services.validator import validate_billing_log

def test_narrative_grounding_verification():
    with open("sample_data/billing_log_2026-07-27.json") as f:
        data = json.load(f)
    valid, _, cid, d = validate_billing_log(data)
    valid_dicts = [v.model_dump() for v in valid]

    reconciliation = compute_reconciliation(valid_dicts, cid, d)
    analytics = compute_analytics(valid_dicts, cid, d)

    narrative_rep = generate_eod_narrative(reconciliation, analytics, provider="deterministic")

    assert narrative_rep.verification_passed is True
    assert narrative_rep.hallucination_count == 0
    assert len(narrative_rep.traced_figures) > 0
    assert "?3,190" in narrative_rep.narrative_text or "3,190" in narrative_rep.narrative_text
    assert "revenue, not profit" in narrative_rep.narrative_text.lower()

def test_hallucination_detection_and_repair():
    """Simulates an LLM producing fabricated/hallucinated numbers."""
    with open("sample_data/billing_log_2026-07-27.json") as f:
        data = json.load(f)
    valid, _, cid, d = validate_billing_log(data)
    valid_dicts = [v.model_dump() for v in valid]

    reconciliation = compute_reconciliation(valid_dicts, cid, d)
    analytics = compute_analytics(valid_dicts, cid, d)

    # Hallucinated text with random numbers like 999999
    fake_text = "Good evening Dr. Mehta! You earned ?999999 profit today from 888 patients."
    _, _, passed, count = verify_and_trace_narrative(fake_text, reconciliation, analytics)
    assert passed is False
    assert count > 0

def test_refunds_day_narrative():
    with open("sample_data/billing_log_2026-07-25.json") as f:
        data = json.load(f)
    valid, _, cid, d = validate_billing_log(data)
    valid_dicts = [v.model_dump() for v in valid]

    reconciliation = compute_reconciliation(valid_dicts, cid, d)
    analytics = compute_analytics(valid_dicts, cid, d)

    narrative_rep = generate_eod_narrative(reconciliation, analytics, provider="deterministic")
    assert narrative_rep.verification_passed is True
    assert "refund" in narrative_rep.narrative_text.lower()
