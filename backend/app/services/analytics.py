from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime
from app.models.schemas import (
    AnalyticsReport, HourlyRevenue, PeakHourInfo,
    MedicineQuantityRank, MedicineRevenueRank
)
from app.services.reconciliation import format_inr
from app.config import settings

def format_hour_12h(hour: int) -> str:
    if hour == 0:
        return "12am"
    elif hour < 12:
        return f"{hour}am"
    elif hour == 12:
        return "12pm"
    else:
        return f"{hour - 12}pm"

def format_hour_range(hour: int) -> str:
    h1 = format_hour_12h(hour)
    h2 = format_hour_12h((hour + 1) % 24)
    return f"{h1}?{h2}"

def compute_analytics(
    visits: List[Dict[str, Any]],
    clinic_id: str,
    date_str: str,
    clinic_name: Optional[str] = None
) -> AnalyticsReport:
    """
    Pure deterministic analytics calculation.
    Computes:
    1. revenue by hour-of-day
    2. top medicines by quantity
    3. top medicines by revenue ? as two distinct rankings
    NEVER calls an LLM. Ground truth.
    """
    hourly_rev = defaultdict(int)
    hourly_visits = defaultdict(int)

    drug_qty = defaultdict(int)
    drug_rev = defaultdict(int)

    for v in visits:
        is_refund = bool(v.get("is_refund", False))
        ts_val = v.get("timestamp")
        if isinstance(ts_val, str):
            dt = datetime.fromisoformat(ts_val.replace("Z", "+00:00"))
        elif isinstance(ts_val, datetime):
            dt = ts_val
        else:
            continue

        hour = dt.hour
        paid = int(v.get("amount_paid_paise", 0))

        if not is_refund:
            hourly_rev[hour] += paid
            hourly_visits[hour] += 1

            for it in v.get("line_items", []):
                name = str(it.get("drug_name", "")).strip().upper()
                if not name:
                    continue
                q = int(it.get("qty", 0))
                price = int(it.get("unit_price_paise", 0))
                drug_qty[name] += q
                drug_rev[name] += q * price

    # Determine hours to display.
    # Default clinic window is 9am (09:00) to 6pm (18:00) if within normal hours,
    # or span of min/max hour recorded if outside.
    recorded_hours = list(hourly_rev.keys())
    if recorded_hours:
        min_h = min(min(recorded_hours), 9)
        max_h = max(max(recorded_hours), 18)
    else:
        min_h = 9
        max_h = 18

    # Find peak hour
    peak_hour_num = None
    max_rev = 0
    for h, rev in hourly_rev.items():
        if rev > max_rev:
            max_rev = rev
            peak_hour_num = h

    hourly_list: List[HourlyRevenue] = []
    for h in range(min_h, max_h + 1):
        rev = hourly_rev[h]
        hourly_list.append(
            HourlyRevenue(
                hour=h,
                hour_label=format_hour_12h(h),
                hour_range=format_hour_range(h),
                revenue_paise=rev,
                revenue_formatted=format_inr(rev),
                visit_count=hourly_visits[h],
                is_peak=(h == peak_hour_num and max_rev > 0)
            )
        )

    peak_hour_info = None
    if peak_hour_num is not None and max_rev > 0:
        hr_range = format_hour_range(peak_hour_num)
        formatted_max = format_inr(max_rev)
        peak_hour_info = PeakHourInfo(
            start_hour=peak_hour_num,
            end_hour=(peak_hour_num + 1) % 24,
            hour_range=hr_range,
            revenue_paise=max_rev,
            revenue_formatted=formatted_max,
            callout_text=f"Peak: {hr_range} ? {formatted_max}"
        )

    # Top medicines by quantity
    sorted_by_qty = sorted(drug_qty.items(), key=lambda x: (-x[1], x[0]))
    top_qty_ranks: List[MedicineQuantityRank] = [
        MedicineQuantityRank(
            rank=idx + 1,
            drug_name=name,
            quantity=q,
            formatted_qty=f"{q} units"
        )
        for idx, (name, q) in enumerate(sorted_by_qty[:10])
    ]

    # Top medicines by revenue
    sorted_by_rev = sorted(drug_rev.items(), key=lambda x: (-x[1], x[0]))
    top_rev_ranks: List[MedicineRevenueRank] = [
        MedicineRevenueRank(
            rank=idx + 1,
            drug_name=name,
            revenue_paise=r,
            formatted_revenue=format_inr(r)
        )
        for idx, (name, r) in enumerate(sorted_by_rev[:10])
    ]

    try:
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        formatted_date = dt.strftime("%d %b %Y")
    except Exception:
        formatted_date = date_str or "N/A"

    resolved_clinic_name = clinic_name or settings.DEFAULT_CLINIC_NAME

    return AnalyticsReport(
        clinic_id=clinic_id or "UNKNOWN",
        clinic_name=resolved_clinic_name,
        date=date_str or "UNKNOWN",
        formatted_date=formatted_date,
        revenue_by_hour=hourly_list,
        peak_hour=peak_hour_info,
        top_medicines_by_quantity=top_qty_ranks,
        top_medicines_by_revenue=top_rev_ranks
    )
