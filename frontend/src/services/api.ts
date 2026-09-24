import {
  ReconciliationReport,
  AnalyticsReport,
  NarrativeReport,
  IngestionResult,
  DaySummary
} from '../types';

const RAW_API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const API_BASE = RAW_API_BASE ? `${RAW_API_BASE}/api` : '/api';

function buildUrl(path: string): URL {
  const fullPath = `${API_BASE}${path}`;
  if (fullPath.startsWith('http://') || fullPath.startsWith('https://')) {
    return new URL(fullPath);
  }
  return new URL(fullPath, window.location.origin);
}

export async function fetchAvailableDays(): Promise<DaySummary[]> {
  const res = await fetch(buildUrl('/ingest/days').toString());
  if (!res.ok) throw new Error('Failed to fetch available days');
  return res.json();
}

export async function seedSampleData(): Promise<{ message: string; datasets: any }> {
  const res = await fetch(buildUrl('/ingest/seed-sample-data').toString(), {
    method: 'POST'
  });
  if (!res.ok) throw new Error('Failed to seed sample datasets');
  return res.json();
}

export async function fetchReconciliation(date: string, clinicId?: string): Promise<ReconciliationReport> {
  const url = buildUrl(`/reconciliation/${date}`);
  if (clinicId) url.searchParams.set('clinic_id', clinicId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch reconciliation for ${date}`);
  return res.json();
}

export async function fetchAnalytics(date: string, clinicId?: string): Promise<AnalyticsReport> {
  const url = buildUrl(`/analytics/${date}`);
  if (clinicId) url.searchParams.set('clinic_id', clinicId);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch analytics for ${date}`);
  return res.json();
}

export async function fetchNarrative(
  date: string,
  clinicId?: string,
  provider: string = 'auto',
  recipient?: string
): Promise<NarrativeReport> {
  const url = buildUrl(`/narrative/${date}`);
  if (clinicId) url.searchParams.set('clinic_id', clinicId);
  if (provider) url.searchParams.set('provider', provider);
  if (recipient) url.searchParams.set('recipient', recipient);
  const res = await fetch(url.toString());
  if (!res.ok) throw new Error(`Failed to fetch narrative for ${date}`);
  return res.json();
}

export async function generateNarrativeCustom(params: {
  date: string;
  clinicId?: string;
  provider?: string;
  apiKey?: string;
  recipient?: string;
}): Promise<NarrativeReport> {
  const res = await fetch(buildUrl('/narrative/generate').toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      date: params.date,
      clinic_id: params.clinicId,
      provider: params.provider || 'auto',
      api_key: params.apiKey,
      custom_recipient: params.recipient
    })
  });
  if (!res.ok) throw new Error('Failed to generate custom narrative');
  return res.json();
}

export async function uploadBillingJson(
  records: any[],
  strict: boolean = false,
  clinicName?: string
): Promise<IngestionResult> {
  const url = buildUrl('/ingest');
  url.searchParams.set('strict', String(strict));
  if (clinicName) url.searchParams.set('clinic_name', clinicName);

  const res = await fetch(url.toString(), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(records)
  });

  const data = await res.json();
  if (!res.ok) {
    throw {
      status: res.status,
      detail: data.detail || data
    };
  }
  return data;
}

export async function uploadBillingFile(
  file: File,
  strict: boolean = false,
  clinicName?: string
): Promise<IngestionResult> {
  const url = buildUrl('/ingest/file');
  url.searchParams.set('strict', String(strict));
  if (clinicName) url.searchParams.set('clinic_name', clinicName);

  const formData = new FormData();
  formData.append('file', file);

  const res = await fetch(url.toString(), {
    method: 'POST',
    body: formData
  });

  const data = await res.json();
  if (!res.ok) {
    throw {
      status: res.status,
      detail: data.detail || data
    };
  }
  return data;
}
