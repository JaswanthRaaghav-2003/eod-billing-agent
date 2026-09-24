from enum import Enum
from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import datetime

class PaymentMode(str, Enum):
    CASH = 'cash'
    CARD = 'card'
    UPI = 'upi'

class LineItem(BaseModel):
    drug_name: str = Field(..., min_length=1, description='Standardized or entered name of the drug')
    qty: int = Field(..., gt=0, description='Quantity prescribed or dispensed, must be > 0')
    unit_price_paise: int = Field(..., ge=0, description='Unit price in integer paise, must be >= 0')

    @field_validator('drug_name')
    @classmethod
    def validate_drug_name(cls, v: str) -> str:
        s = v.strip()
        if not s:
            raise ValueError('drug_name cannot be empty or whitespace')
        return s.upper()

class VisitRecord(BaseModel):
    clinic_id: str = Field(..., min_length=1, description='Clinic identifier, e.g. CLN-KNP-014')
    visit_id: str = Field(..., min_length=1, description='Unique visit identifier, e.g. V-20260727-001')
    timestamp: datetime = Field(..., description='ISO 8601 UTC timestamp of the visit')
    doctor_id: Optional[str] = Field(None, description='Doctor ID')
    line_items: List[LineItem] = Field(..., min_length=1, description='List of billed line items')
    payment_mode: PaymentMode = Field(..., description='Mode of payment: cash, card, or upi')
    amount_paid_paise: int = Field(..., description='Amount paid in integer paise (negative for refunds)')
    discount_paise: int = Field(default=0, ge=0, description='Discount given in integer paise')
    is_refund: bool = Field(default=False, description='True if this is a refund adjustment')

    @model_validator(mode='after')
    def validate_refund_consistency(self):
        if self.is_refund:
            if self.amount_paid_paise > 0:
                raise ValueError(
                    f'Refund record amount_paid_paise must be negative or zero, but got {self.amount_paid_paise}'
                )
        else:
            if self.amount_paid_paise < 0:
                raise ValueError(
                    f'Non-refund record amount_paid_paise cannot be negative, got {self.amount_paid_paise}'
                )
        return self

class ValidationErrorDetail(BaseModel):
    row_index: int
    visit_id: Optional[str] = None
    field: str
    error: str
    actionable_guidance: str

class IngestionResult(BaseModel):
    status: str
    message: str
    date: Optional[str] = None
    clinic_id: Optional[str] = None
    total_rows: int
    valid_rows_count: int
    malformed_rows_count: int
    validation_errors: List[ValidationErrorDetail] = []

class PaymentModeBreakdown(BaseModel):
    mode: str
    billed_paise: int
    billed_formatted: str
    collected_paise: int
    collected_formatted: str
    outstanding_paise: int
    outstanding_formatted: str
    refunds_paise: int
    refunds_formatted: str

class ReconciliationReport(BaseModel):
    clinic_id: str
    clinic_name: str
    date: str
    formatted_date: str
    total_visits: int
    refund_visits: int
    pending_invoices_count: int
    total_billed_paise: int
    total_billed_formatted: str
    total_collected_paise: int
    total_collected_formatted: str
    collection_percentage: float
    collection_percentage_formatted: str
    total_outstanding_paise: int
    total_outstanding_formatted: str
    total_refunds_paise: int
    total_refunds_formatted: str
    payment_mode_breakdown: List[PaymentModeBreakdown]
    totals_row: PaymentModeBreakdown

class HourlyRevenue(BaseModel):
    hour: int
    hour_label: str
    hour_range: str
    revenue_paise: int
    revenue_formatted: str
    visit_count: int
    is_peak: bool

class PeakHourInfo(BaseModel):
    start_hour: int
    end_hour: int
    hour_range: str
    revenue_paise: int
    revenue_formatted: str
    callout_text: str

class MedicineQuantityRank(BaseModel):
    rank: int
    drug_name: str
    quantity: int
    formatted_qty: str

class MedicineRevenueRank(BaseModel):
    rank: int
    drug_name: str
    revenue_paise: int
    formatted_revenue: str

class AnalyticsReport(BaseModel):
    clinic_id: str
    clinic_name: str
    date: str
    formatted_date: str
    revenue_by_hour: List[HourlyRevenue]
    peak_hour: Optional[PeakHourInfo] = None
    top_medicines_by_quantity: List[MedicineQuantityRank]
    top_medicines_by_revenue: List[MedicineRevenueRank]

class TracedFigure(BaseModel):
    figure_text: str
    field_path: str
    report_value: Any
    is_verified: bool
    context: Optional[str] = None

class UncomputableMetric(BaseModel):
    metric: str
    reason: str

class NarrativeReport(BaseModel):
    clinic_id: str
    clinic_name: str
    date: str
    formatted_date: str
    recipient: str
    channel: str
    narrative_text: str
    traced_figures: List[TracedFigure]
    uncomputable_metrics: List[UncomputableMetric]
    status: str = 'SUCCESS'
    llm_source: str = 'grounded_engine'
    verification_passed: bool = True
    hallucination_count: int = 0

class NarrativeGenerateRequest(BaseModel):
    clinic_id: Optional[str] = None
    date: Optional[str] = None
    provider: Optional[str] = 'auto' # 'auto', 'gemini', 'openai', 'deterministic'
    api_key: Optional[str] = None
    custom_recipient: Optional[str] = None
