from typing import List, Dict, Any, Optional
from app.models.schemas import (
    VisitRecord, ReconciliationReport, PaymentModeBreakdown, PaymentMode
)
from app.config import settings

def format_inr(paise: int) -> str:
    sign = "-" if paise < 0 else ""
    abs_paise = abs(paise)
    rupees = abs_paise // 100
    rem = abs_paise % 100

    s = str(rupees)
    if len(s) > 3:
        last3 = s[-3:]
        rest = s[:-3]
        parts = []
        while len(rest) > 2:
            parts.insert(0, rest[-2:])
            rest = rest[:-2]
        if rest:
            parts.insert(0, rest)
        formatted_rupees = ",".join(parts) + "," + last3
    else:
        formatted_rupees = s

    if rem > 0:
        return f"{sign}?{formatted_rupees}.{rem:02d}"
    return f"{sign}?{formatted_rupees}"

def compute_reconciliation(
    visits: List[Dict[str, Any]],
    clinic_id: str,
    date_str: str,
    clinic_name: Optional[str] = None
) -> ReconciliationReport:
    """
    Pure deterministic EOD reconciliation calculation.
    Computes: total billed, total collected, outstanding, and refunds ? each split by payment mode.
    Store money as integer paise throughout.
    NEVER calls an LLM. Ground truth.
    """
    modes = ["cash", "card", "upi"]
    mode_data = {
        m: {
            "billed_paise": 0,
            "collected_paise": 0,
            "outstanding_paise": 0,
            "refunds_paise": 0,
            "sales_visits": 0,
            "refund_visits": 0,
            "pending_visits": 0
        }
        for m in modes
    }

    total_sales_visits = 0
    total_refund_visits = 0
    total_pending_visits = 0

    for v in visits:
        m = str(v.get("payment_mode", "cash")).lower()
        if m not in mode_data:
            m = "cash"

        is_refund = bool(v.get("is_refund", False))
        paid = int(v.get("amount_paid_paise", 0))
        disc = int(v.get("discount_paise", 0))

        items_sum = sum(
            int(it.get("qty", 0)) * int(it.get("unit_price_paise", 0))
            for it in v.get("line_items", [])
        )

        if is_refund:
            mode_data[m]["refund_visits"] += 1
            total_refund_visits += 1
            refund_amount = abs(paid) if paid != 0 else items_sum
            mode_data[m]["refunds_paise"] += refund_amount
        else:
            mode_data[m]["sales_visits"] += 1
            total_sales_visits += 1

            net_billed = max(0, items_sum - disc)
            mode_data[m]["billed_paise"] += net_billed
            mode_data[m]["collected_paise"] += paid

            outstanding = max(0, net_billed - paid)
            mode_data[m]["outstanding_paise"] += outstanding
            if outstanding > 0:
                mode_data[m]["pending_visits"] += 1
                total_pending_visits += 1

    breakdowns: List[PaymentModeBreakdown] = []
    tot_billed = 0
    tot_collected = 0
    tot_outstanding = 0
    tot_refunds = 0

    mode_display_names = {
        "cash": "Cash",
        "card": "Card",
        "upi": "UPI"
    }

    for m in modes:
        d = mode_data[m]
        tot_billed += d["billed_paise"]
        tot_collected += d["collected_paise"]
        tot_outstanding += d["outstanding_paise"]
        tot_refunds += d["refunds_paise"]

        breakdowns.append(
            PaymentModeBreakdown(
                mode=mode_display_names[m],
                billed_paise=d["billed_paise"],
                billed_formatted=format_inr(d["billed_paise"]),
                collected_paise=d["collected_paise"],
                collected_formatted=format_inr(d["collected_paise"]),
                outstanding_paise=d["outstanding_paise"],
                outstanding_formatted=format_inr(d["outstanding_paise"]),
                refunds_paise=d["refunds_paise"],
                refunds_formatted=format_inr(d["refunds_paise"]),
            )
        )

    if tot_billed > 0:
        collection_pct = round((tot_collected / tot_billed) * 100, 1)
    else:
        collection_pct = 0.0

    totals_row = PaymentModeBreakdown(
        mode="Total",
        billed_paise=tot_billed,
        billed_formatted=format_inr(tot_billed),
        collected_paise=tot_collected,
        collected_formatted=format_inr(tot_collected),
        outstanding_paise=tot_outstanding,
        outstanding_formatted=format_inr(tot_outstanding),
        refunds_paise=tot_refunds,
        refunds_formatted=format_inr(tot_refunds),
    )

    try:
        from datetime import datetime
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")
    except Exception:
        formatted_date = date_str or "N/A"

    resolved_clinic_name = clinic_name or settings.DEFAULT_CLINIC_NAME

    pct_str = f"{collection_pct:.0f}% of billed" if collection_pct.is_integer() else f"{collection_pct:.1f}% of billed"

    return ReconciliationReport(
        clinic_id=clinic_id or "UNKNOWN",
        clinic_name=resolved_clinic_name,
        date=date_str or "UNKNOWN",
        formatted_date=formatted_date,
        total_visits=total_sales_visits,
        refund_visits=total_refund_visits,
        pending_invoices_count=total_pending_visits,
        total_billed_paise=tot_billed,
        total_billed_formatted=format_inr(tot_billed),
        total_collected_paise=tot_collected,
        total_collected_formatted=format_inr(tot_collected),
        collection_percentage=collection_pct,
        collection_percentage_formatted=pct_str,
        total_outstanding_paise=tot_outstanding,
        total_outstanding_formatted=format_inr(tot_outstanding),
        total_refunds_paise=tot_refunds,
        total_refunds_formatted=format_inr(tot_refunds),
        payment_mode_breakdown=breakdowns,
        totals_row=totals_row
    )
