from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime
from app.models.schemas import VisitRecord, LineItem, ValidationErrorDetail, PaymentMode

def validate_line_item(item_data: Any, item_idx: int, visit_id: str, row_idx: int) -> Tuple[Optional[LineItem], Optional[ValidationErrorDetail]]:
    if not isinstance(item_data, dict):
        return None, ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field=f"line_items[{item_idx}]",
            error="Line item must be an object/dictionary.",
            actionable_guidance="Ensure each item in 'line_items' is formatted as {drug_name, qty, unit_price_paise}."
        )

    drug_name = item_data.get("drug_name")
    if not drug_name or not isinstance(drug_name, str) or not drug_name.strip():
        return None, ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field=f"line_items[{item_idx}].drug_name",
            error="Missing or empty drug_name in line item.",
            actionable_guidance="Provide a valid, non-empty drug name string."
        )

    qty = item_data.get("qty")
    if qty is None or not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
        return None, ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field=f"line_items[{item_idx}].qty",
            error=f"Invalid quantity '{qty}'. Must be an integer greater than 0.",
            actionable_guidance="Provide positive integer quantity (e.g. qty: 1)."
        )

    unit_price = item_data.get("unit_price_paise")
    if unit_price is None or not isinstance(unit_price, int) or isinstance(unit_price, bool) or unit_price < 0:
        return None, ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field=f"line_items[{item_idx}].unit_price_paise",
            error=f"Invalid unit_price_paise '{unit_price}'. Must be a non-negative integer.",
            actionable_guidance="Provide integer paise for unit_price (e.g. unit_price_paise: 4000)."
        )

    return LineItem(drug_name=drug_name.strip().upper(), qty=qty, unit_price_paise=unit_price), None

def validate_visit_record(record_data: Any, row_idx: int) -> Tuple[Optional[VisitRecord], List[ValidationErrorDetail]]:
    errors: List[ValidationErrorDetail] = []
    if not isinstance(record_data, dict):
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=None,
            field="root",
            error="Record must be a JSON object.",
            actionable_guidance="Provide each row as a key-value object matching the billing schema."
        ))
        return None, errors

    visit_id = record_data.get("visit_id")
    if not visit_id or not isinstance(visit_id, str) or not visit_id.strip():
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=str(visit_id) if visit_id else None,
            field="visit_id",
            error="Missing or invalid visit_id.",
            actionable_guidance="Specify a unique non-empty string identifier for the visit (e.g., 'V-20260727-001')."
        ))

    clinic_id = record_data.get("clinic_id")
    if not clinic_id or not isinstance(clinic_id, str) or not clinic_id.strip():
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="clinic_id",
            error="Missing or invalid clinic_id.",
            actionable_guidance="Specify the clinic code (e.g., 'CLN-KNP-014')."
        ))

    ts_raw = record_data.get("timestamp")
    parsed_ts = None
    if not ts_raw or not isinstance(ts_raw, str):
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="timestamp",
            error="Missing or invalid timestamp.",
            actionable_guidance="Provide an ISO 8601 UTC timestamp string (e.g., '2026-07-27T09:10:00Z')."
        ))
    else:
        try:
            parsed_ts = datetime.fromisoformat(ts_raw.replace("Z", "+00:00"))
        except Exception as e:
            errors.append(ValidationErrorDetail(
                row_index=row_idx,
                visit_id=visit_id,
                field="timestamp",
                error=f"Unparseable ISO 8601 timestamp '{ts_raw}': {str(e)}",
                actionable_guidance="Ensure timestamp matches ISO 8601 UTC format, e.g. 'YYYY-MM-DDTHH:MM:SSZ'."
            ))

    payment_mode_raw = record_data.get("payment_mode")
    parsed_mode = None
    if payment_mode_raw is None:
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="payment_mode",
            error="Missing required field 'payment_mode'.",
            actionable_guidance="Specify a payment_mode enum: 'cash', 'card', or 'upi'."
        ))
    elif not isinstance(payment_mode_raw, str) or payment_mode_raw.lower() not in ["cash", "card", "upi"]:
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="payment_mode",
            error=f"Invalid payment_mode '{payment_mode_raw}'. Must be 'cash', 'card', or 'upi'.",
            actionable_guidance="Change payment_mode to one of the accepted values: 'cash', 'card', or 'upi'."
        ))
    else:
        parsed_mode = PaymentMode(payment_mode_raw.lower())

    amount_paid = record_data.get("amount_paid_paise")
    if amount_paid is None or not isinstance(amount_paid, int) or isinstance(amount_paid, bool):
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="amount_paid_paise",
            error=f"Invalid or missing amount_paid_paise '{amount_paid}'. Must be an integer representing paise.",
            actionable_guidance="Provide integer paise (not float rupees), e.g. 5000 for ?50.00."
        ))

    discount_paise = record_data.get("discount_paise", 0)
    if discount_paise is None or not isinstance(discount_paise, int) or isinstance(discount_paise, bool) or discount_paise < 0:
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="discount_paise",
            error=f"Invalid discount_paise '{discount_paise}'. Must be a non-negative integer.",
            actionable_guidance="Provide integer paise for discount, or 0 if no discount."
        ))

    is_refund = record_data.get("is_refund", False)
    if not isinstance(is_refund, bool):
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="is_refund",
            error=f"Invalid is_refund '{is_refund}'. Must be boolean true or false.",
            actionable_guidance="Set is_refund to true for refund adjustments, false otherwise."
        ))

    # Consistency rule: refund amount must be negative adjustment
    if isinstance(amount_paid, int) and not isinstance(amount_paid, bool) and isinstance(is_refund, bool):
        if is_refund and amount_paid > 0:
            errors.append(ValidationErrorDetail(
                row_index=row_idx,
                visit_id=visit_id,
                field="amount_paid_paise",
                error=f"Refund record cannot have positive amount_paid_paise ({amount_paid}).",
                actionable_guidance="Set amount_paid_paise to a negative value on refund rows (money going out)."
            ))
        elif not is_refund and amount_paid < 0:
            errors.append(ValidationErrorDetail(
                row_index=row_idx,
                visit_id=visit_id,
                field="amount_paid_paise",
                error=f"Non-refund record cannot have negative amount_paid_paise ({amount_paid}).",
                actionable_guidance="Set amount_paid_paise to a positive value or 0 for normal sales/consultations."
            ))

    raw_items = record_data.get("line_items")
    valid_items: List[LineItem] = []
    if raw_items is None or not isinstance(raw_items, list) or len(raw_items) == 0:
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="line_items",
            error="line_items must be a non-empty array of items.",
            actionable_guidance="Provide at least one line item with drug_name, qty, and unit_price_paise."
        ))
    else:
        for idx, item in enumerate(raw_items):
            parsed_item, item_err = validate_line_item(item, idx, visit_id or f"row-{row_idx}", row_idx)
            if item_err:
                errors.append(item_err)
            elif parsed_item:
                valid_items.append(parsed_item)

    if errors:
        return None, errors

    try:
        visit_record = VisitRecord(
            clinic_id=clinic_id.strip(),
            visit_id=visit_id.strip(),
            timestamp=parsed_ts,
            doctor_id=record_data.get("doctor_id"),
            line_items=valid_items,
            payment_mode=parsed_mode,
            amount_paid_paise=amount_paid,
            discount_paise=discount_paise if discount_paise is not None else 0,
            is_refund=is_refund
        )
        return visit_record, []
    except Exception as e:
        errors.append(ValidationErrorDetail(
            row_index=row_idx,
            visit_id=visit_id,
            field="schema",
            error=str(e),
            actionable_guidance="Check that record matches all schema constraints."
        ))
        return None, errors

def validate_billing_log(records: List[Any]) -> Tuple[List[VisitRecord], List[ValidationErrorDetail], Optional[str], Optional[str]]:
    valid_records: List[VisitRecord] = []
    all_errors: List[ValidationErrorDetail] = []
    clinic_ids = set()
    dates = set()

    for idx, rec in enumerate(records):
        valid_rec, errs = validate_visit_record(rec, row_idx=idx + 1)
        if errs:
            all_errors.extend(errs)
        if valid_rec:
            valid_records.append(valid_rec)
            clinic_ids.add(valid_rec.clinic_id)
            dates.add(valid_rec.timestamp.strftime("%Y-%m-%d"))

    clinic_id = next(iter(clinic_ids)) if clinic_ids else None
    date_str = next(iter(dates)) if dates else None

    return valid_records, all_errors, clinic_id, date_str
