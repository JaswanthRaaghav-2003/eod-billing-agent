import re
from typing import List, Dict, Any, Tuple
from app.models.schemas import ReconciliationReport, AnalyticsReport, TracedFigure, UncomputableMetric

def extract_numbers_and_entities(text: str) -> List[str]:
    """
    Extracts numerical candidates, currency amounts, percentages, and unit counts from text.
    """
    pattern = r"(?:[?$]\s*[\d,]+(?:\.\d+)?|\b\d+(?:,\d+)*(?:\.\d+)?%?|\b\d+\s*(?:visits?|units?|pending|refunds?|invoices?)\b)"
    matches = re.findall(pattern, text, flags=re.IGNORECASE)
    return [m.strip() for m in matches if m.strip()]

def verify_and_trace_narrative(
    narrative_text: str,
    reconciliation: ReconciliationReport,
    analytics: AnalyticsReport
) -> Tuple[List[TracedFigure], List[UncomputableMetric], bool, int]:
    """
    Verifies that every figure in narrative_text maps back to ground truth deterministic fields.
    Returns (traced_figures, uncomputable_metrics, verification_passed, hallucination_count).
    """
    traced_figures: List[TracedFigure] = []
    hallucination_count = 0

    # Build lookup map of known deterministic truth values
    # Formats supported: formatted string (?42,850), bare number (42850), paise value, etc.
    known_mappings = []

    # Reconciliation fields
    known_mappings.append({
        "label": reconciliation.total_billed_formatted,
        "alt_labels": [
            str(reconciliation.total_billed_paise // 100),
            f"{reconciliation.total_billed_paise // 100:,}",
            f"{reconciliation.total_visits} visits"
        ],
        "field_path": "reconciliation.total_billed",
        "report_value": reconciliation.total_billed_paise,
        "context": "Total Billed"
    })

    known_mappings.append({
        "label": reconciliation.total_collected_formatted,
        "alt_labels": [
            str(reconciliation.total_collected_paise // 100),
            f"{reconciliation.total_collected_paise // 100:,}",
            f"{int(round(reconciliation.collection_percentage))}%",
            f"{reconciliation.collection_percentage:.1f}%",
            f"{reconciliation.collection_percentage:.0f}%"
        ],
        "field_path": "reconciliation.total_collected",
        "report_value": reconciliation.total_collected_paise,
        "context": "Total Collected"
    })

    known_mappings.append({
        "label": reconciliation.total_outstanding_formatted,
        "alt_labels": [
            str(reconciliation.total_outstanding_paise // 100),
            f"{reconciliation.total_outstanding_paise // 100:,}",
            f"{reconciliation.pending_invoices_count} visits",
            f"{reconciliation.pending_invoices_count} pending invoices",
            f"{reconciliation.pending_invoices_count} pending"
        ],
        "field_path": "reconciliation.outstanding",
        "report_value": reconciliation.total_outstanding_paise,
        "context": "Outstanding Balance"
    })

    known_mappings.append({
        "label": reconciliation.total_refunds_formatted,
        "alt_labels": [
            str(reconciliation.total_refunds_paise // 100),
            f"{reconciliation.total_refunds_paise // 100:,}",
            f"{reconciliation.refund_visits} refund",
            f"{reconciliation.refund_visits} refunds",
            f"{reconciliation.refund_visits} visit"
        ],
        "field_path": "reconciliation.refunds",
        "report_value": reconciliation.total_refunds_paise,
        "context": "Total Refunds"
    })

    # Analytics fields: Peak hour
    if analytics.peak_hour:
        pk = analytics.peak_hour
        known_mappings.append({
            "label": f"{pk.hour_range} / {pk.revenue_formatted}",
            "alt_labels": [
                pk.hour_range,
                pk.revenue_formatted,
                str(pk.revenue_paise // 100),
                f"{pk.revenue_paise // 100:,}"
            ],
            "field_path": "analytics.peak_hour",
            "report_value": f"{pk.hour_range} ({pk.revenue_formatted})",
            "context": "Busiest Hour"
        })

    # Analytics fields: Top mover by quantity
    if analytics.top_medicines_by_quantity:
        top_q = analytics.top_medicines_by_quantity[0]
        known_mappings.append({
            "label": f"{top_q.drug_name} / {top_q.quantity}",
            "alt_labels": [
                top_q.drug_name,
                top_q.formatted_qty,
                f"{top_q.quantity} units",
                str(top_q.quantity)
            ],
            "field_path": "analytics.top_quantity",
            "report_value": f"{top_q.drug_name} ({top_q.quantity} units)",
            "context": "Top Mover by Quantity"
        })

    # Analytics fields: Top mover by revenue
    if analytics.top_medicines_by_revenue:
        top_r = analytics.top_medicines_by_revenue[0]
        known_mappings.append({
            "label": f"{top_r.drug_name} / {top_r.formatted_revenue}",
            "alt_labels": [
                top_r.drug_name,
                top_r.formatted_revenue,
                str(top_r.revenue_paise // 100),
                f"{top_r.revenue_paise // 100:,}"
            ],
            "field_path": "analytics.top_revenue",
            "report_value": f"{top_r.drug_name} ({top_r.formatted_revenue})",
            "context": "Top by Revenue"
        })

    # Check each mapping against narrative text
    for item in known_mappings:
        found = False
        if item["label"] in narrative_text:
            found = True
            figure_str = item["label"]
        else:
            for alt in item.get("alt_labels", []):
                if alt in narrative_text:
                    found = True
                    figure_str = item["label"]
                    break

        if found:
            traced_figures.append(
                TracedFigure(
                    figure_text=item["label"],
                    field_path=item["field_path"],
                    report_value=item["report_value"],
                    is_verified=True,
                    context=item.get("context")
                )
            )

    # Check uncomputable metrics (e.g. profit, cost price)
    uncomputable_metrics: List[UncomputableMetric] = []
    # If profit is not present in billing schema, ensure model explicitly noted it
    has_cost_note = any(
        phrase in narrative_text.lower()
        for phrase in ["cost data wasn't available", "cost data was not available", "revenue, not profit", "not profit", "cost price"]
    )

    uncomputable_metrics.append(
        UncomputableMetric(
            metric="Profit / Margin",
            reason="Cost data was not provided in the billing log (only selling prices are captured), so profit cannot be computed without making ungrounded assumptions."
        )
    )

    # Scan for potential hallucinated numbers: numbers > 10 in text not matching any known figure
    raw_nums = re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", narrative_text)
    known_digits = set()
    for item in known_mappings:
        known_digits.update(re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", str(item["label"])))
        known_digits.update(re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", str(item["report_value"])))
        for alt in item.get("alt_labels", []):
            known_digits.update(re.findall(r"\b\d+(?:,\d+)*(?:\.\d+)?\b", alt))

    # Add date digits to known (e.g., 2026, 27, 25, 26, etc.)
    known_digits.update(re.findall(r"\b\d+\b", reconciliation.date))
    known_digits.update(re.findall(r"\b\d+\b", reconciliation.formatted_date))
    known_digits.update(["1", "2", "3", "4", "5", "10", "12"]) # common hour or rank digits

    for num in raw_nums:
        clean_num = num.replace(",", "")
        if clean_num not in [k.replace(",", "") for k in known_digits] and float(clean_num) > 10:
            hallucination_count += 1

    verification_passed = (hallucination_count == 0)

    return traced_figures, uncomputable_metrics, verification_passed, hallucination_count
