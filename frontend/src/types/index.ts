export interface PaymentModeBreakdown {
  mode: string;
  billed_paise: number;
  billed_formatted: string;
  collected_paise: number;
  collected_formatted: string;
  outstanding_paise: number;
  outstanding_formatted: string;
  refunds_paise: number;
  refunds_formatted: string;
}

export interface ReconciliationReport {
  clinic_id: string;
  clinic_name: string;
  date: string;
  formatted_date: string;
  total_visits: number;
  refund_visits: number;
  pending_invoices_count: number;
  total_billed_paise: number;
  total_billed_formatted: string;
  total_collected_paise: number;
  total_collected_formatted: string;
  collection_percentage: number;
  collection_percentage_formatted: string;
  total_outstanding_paise: number;
  total_outstanding_formatted: string;
  total_refunds_paise: number;
  total_refunds_formatted: string;
  payment_mode_breakdown: PaymentModeBreakdown[];
  totals_row: PaymentModeBreakdown;
}

export interface HourlyRevenue {
  hour: number;
  hour_label: string;
  hour_range: string;
  revenue_paise: number;
  revenue_formatted: string;
  visit_count: number;
  is_peak: boolean;
}

export interface PeakHourInfo {
  start_hour: number;
  end_hour: number;
  hour_range: string;
  revenue_paise: number;
  revenue_formatted: string;
  callout_text: string;
}

export interface MedicineQuantityRank {
  rank: number;
  drug_name: string;
  quantity: number;
  formatted_qty: string;
}

export interface MedicineRevenueRank {
  rank: number;
  drug_name: string;
  revenue_paise: number;
  formatted_revenue: string;
}

export interface AnalyticsReport {
  clinic_id: string;
  clinic_name: string;
  date: string;
  formatted_date: string;
  revenue_by_hour: HourlyRevenue[];
  peak_hour: PeakHourInfo | null;
  top_medicines_by_quantity: MedicineQuantityRank[];
  top_medicines_by_revenue: MedicineRevenueRank[];
}

export interface TracedFigure {
  figure_text: string;
  field_path: string;
  report_value: any;
  is_verified: boolean;
  context?: string;
}

export interface UncomputableMetric {
  metric: string;
  reason: string;
}

export interface NarrativeReport {
  clinic_id: string;
  clinic_name: string;
  date: string;
  formatted_date: string;
  recipient: string;
  channel: string;
  narrative_text: string;
  traced_figures: TracedFigure[];
  uncomputable_metrics: UncomputableMetric[];
  status: string;
  llm_source: string;
  verification_passed: boolean;
  hallucination_count: number;
}

export interface ValidationErrorDetail {
  row_index: number;
  visit_id?: string;
  field: string;
  error: string;
  actionable_guidance: string;
}

export interface IngestionResult {
  status: string;
  message: string;
  date?: string;
  clinic_id?: string;
  total_rows: number;
  valid_rows_count: number;
  malformed_rows_count: number;
  validation_errors: ValidationErrorDetail[];
}

export interface DaySummary {
  date: string;
  clinic_id: string;
  clinic_name?: string;
  total_visits: number;
  sales_visits: number;
  refund_visits: number;
  total_collected_paise?: number;
}
