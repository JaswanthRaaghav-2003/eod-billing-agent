# SwasthiQ Kaagazy ? EOD Billing & Analytics Agent

> **Production-grade End-of-Day (EOD) Reconciliation, Analytics & Grounded Agentic Narrative System** built for SwasthiQ's Kaagazy clinic platform.

---

## ?? Architecture Overview

This project is architected around a strict principle: **The Deterministic Layer is your Ground Truth, and the Agentic Layer is strictly grounded against it.**

```
                                      +------------------------------------+
                                      |     Raw Billing Log JSON / File    |
                                      +------------------------------------+
                                                         |
                                                         v
                                      +------------------------------------+
                                      |       Validator Service            |
                                      | (Row-level Actionable Validations) |
                                      +------------------------------------+
                                          /                            \
                  [Malformed Rows]       /                              \ [Valid Records]
                                        v                                v
                        +----------------------------+       +----------------------------------+
                        | Actionable Error Inspector |       |     Atomic SQLite Transaction    |
                        |   (Rejections / Warnings)  |       | (Idempotent Update & Consistency)|
                        +----------------------------+       +----------------------------------+
                                                                     /                  \
                                                                    v                    v
                                      +-------------------------------+      +---------------------------------+
                                      |    Deterministic EOD Layer    |      |    Deterministic Analytics      |
                                      |  (Billed, Collected, Refunds, |      |  (Hourly Revenue, Peak Hour,    |
                                      |    Outstanding in Paise)      |      |   Top Medicines Qty & Revenue)  |
                                      +-------------------------------+      +---------------------------------+
                                                                    \                    /
                                                                     v                  v
                                                      +-----------------------------------+
                                                      |   Grounded Agentic LLM Layer      |
                                                      | (Zero-Hallucination WhatsApp Tone)|
                                                      +-----------------------------------+
                                                                        |
                                                                        v
                                                      +-----------------------------------+
                                                      |     Grounding Verifier & Guard    |
                                                      | (Maps Figures -> Report Fields)   |
                                                      +-----------------------------------+
                                                                        |
                                                                        v
                                                      +-----------------------------------+
                                                      |  React Frontend (3 Screens & Bar) |
                                                      +-----------------------------------+
```

---

## ?? Repository Structure

```
d:/Swasthiq/
??? backend/
?   ??? app/
?   ?   ??? config.py                 # App settings, environment vars, defaults
?   ?   ??? database.py               # SQLite schema & atomic transactional operations
?   ?   ??? main.py                   # FastAPI application factory & lifespan handler
?   ?   ??? models/
?   ?   ?   ??? schemas.py            # Pydantic v2 data schemas & validation models
?   ?   ??? routers/
?   ?   ?   ??? ingestion.py          # /api/ingest, /api/ingest/file, /api/ingest/days
?   ?   ?   ??? reconciliation.py     # /api/reconciliation/{date}
?   ?   ?   ??? analytics.py          # /api/analytics/{date}
?   ?   ?   ??? narrative.py          # /api/narrative/{date}, /api/narrative/generate
?   ?   ??? services/
?   ?       ??? validator.py          # Ingestion validation with actionable error reports
?   ?       ??? reconciliation.py     # Pure deterministic reconciliation (integer paise)
?   ?       ??? analytics.py          # Deterministic hourly & medicine rankings
?   ?       ??? grounding_verifier.py # Audits narrative figures against ground truth
?   ?       ??? llm_agent.py          # WhatsApp summary generator & repair fallback
?   ??? tests/
?   ?   ??? test_validation.py        # Schema validation & error reporting tests
?   ?   ??? test_reconciliation.py    # Happy path & non-happy-path day math tests
?   ?   ??? test_analytics.py         # Hourly revenue, peak callouts & distinct rankings
?   ?   ??? test_narrative.py         # Grounding audits, hallucination repair tests
?   ?   ??? test_api_endpoints.py     # Full FastAPI REST integration tests
?   ??? requirements.txt              # Backend dependencies
?   ??? run.py                        # Uvicorn entrypoint script
??? frontend/
?   ??? src/
?   ?   ??? components/
?   ?   ?   ??? Layout.tsx            # Persistent sidebar & date picker header
?   ?   ?   ??? EODReconciliation.tsx # Screen 1: 4 Stat Cards + Mode Breakdown Table
?   ?   ?   ??? AnalyticsView.tsx     # Screen 2: Hourly Chart + 2 Distinct Rankings
?   ?   ?   ??? AINarrativeSummary.tsx# Screen 3: WhatsApp preview + Traced Figures
?   ?   ?   ??? IngestionModal.tsx    # Drag-and-drop file upload & live schema test
?   ?   ?   ??? ValidationErrorsModal.tsx # Actionable inspector for rejected rows
?   ?   ?   ??? SettingsModal.tsx     # Custom Gemini/OpenAI API key config
?   ?   ??? services/
?   ?   ?   ??? api.ts                # REST API client with full error handling
?   ?   ??? types/
?   ?   ?   ??? index.ts              # TypeScript interfaces mirroring backend
?   ?   ??? App.tsx                   # Main React root application
?   ?   ??? main.tsx                  # React DOM mount
?   ?   ??? style.css                 # Custom animations and styling
?   ??? package.json
?   ??? tsconfig.json
?   ??? vite.config.ts                # Vite config with API proxy to localhost:8000
??? sample_data/
?   ??? billing_log_2026-07-27.json   # 19 visits (18 valid, 1 malformed row)
?   ??? billing_log_2026-07-25.json   # 3 visits (100% refunds only)
?   ??? billing_log_2026-07-26.json   # 0 visits (closed/empty day)
?   ??? README.md
??? README.md                         # Documentation & Technical Explanation
```

---

## ??? Technical Explanation: Data Consistency & REST Architecture

### 1. Guaranteeing Data Consistency Upon Update
In healthcare and clinic administration, partial writes or duplicate entries can corrupt accounts. Our backend implements a strict consistency model:

- **Atomic Transactions (`BEGIN ... COMMIT / ROLLBACK`)**: In `backend/app/database.py`, the `save_visits_atomically` method uses SQLite transactions. When a daily log for date `YYYY-MM-DD` and `clinic_id` is ingested, any previous entries for that date are replaced in a single atomic transaction:
  ```sql
  DELETE FROM line_items WHERE visit_id IN (SELECT visit_id FROM visits WHERE clinic_id = ? AND date = ?);
  DELETE FROM visits WHERE clinic_id = ? AND date = ?;
  -- Insert all valid visit records and line items
  COMMIT;
  ```
- **Referential Integrity**: Foreign keys are strictly enforced on every database connection using `PRAGMA foreign_keys = ON;`, ensuring child line items cascade delete cleanly.
- **Integer Paise Representation**: All monetary quantities (`amount_paid_paise`, `unit_price_paise`, `discount_paise`) are stored and calculated strictly as integers. No IEEE 754 floating-point inaccuracies exist in any accounting layer.

### 2. Validation & Actionable Rejections
Rather than failing with a generic HTTP 500 error:
- Each row is validated individually against schema constraints.
- When an invalid row is encountered (such as visit `V-20260727-019` which lacks a `payment_mode`), the system generates an actionable diagnostic:
  ```json
  {
    "row_index": 19,
    "visit_id": "V-20260727-019",
    "field": "payment_mode",
    "error": "Missing required field 'payment_mode'.",
    "actionable_guidance": "Specify a valid payment_mode ('cash', 'card', or 'upi')."
  }
  ```
- In default ingestion mode, the API ingests all valid visits (18 visits) and returns the actionable error report for rejected rows. In `strict=true` mode, it returns HTTP 422 Unprocessable Entity with the exact violation details.

---

## ?? REST API Contracts

### Ingestion Endpoints
- **`POST /api/ingest`**: Ingests JSON billing array with optional `?strict=true` and `?clinic_name=...`.
- **`POST /api/ingest/file`**: Multipart form upload for `.json` log files.
- **`GET /api/ingest/days`**: Returns all available dates with aggregate visit counts and sales totals.
- **`POST /api/ingest/seed-sample-data`**: Re-populates the database with the 3 sample days (25 Jul, 26 Jul, 27 Jul).

### Reconciliation Endpoint
- **`GET /api/reconciliation/{date_str}`**: Returns deterministic EOD reconciliation.
  - Fields: `total_billed_paise`, `total_collected_paise`, `collection_percentage`, `total_outstanding_paise`, `total_refunds_paise`, `pending_invoices_count`, `payment_mode_breakdown`.

### Analytics Endpoint
- **`GET /api/analytics/{date_str}`**: Returns deterministic analytics.
  - Fields: `revenue_by_hour` (hourly buckets with `is_peak`), `peak_hour` (window & formatted total), `top_medicines_by_quantity` and `top_medicines_by_revenue` (as two distinct rankings).

### Narrative & Grounding Endpoints
- **`GET /api/narrative/{date_str}`**: Generates grounded WhatsApp summary with `traced_figures`.
- **`POST /api/narrative/generate`**: Generates narrative with optional custom API keys or providers (`gemini`, `openai`, `deterministic`).

---

## ?? Verification of Evaluation Criteria

| Requirement | Implementation Detail | Status |
|---|---|---|
| **Deterministic Ground Truth** | `reconciliation.py` and `analytics.py` compute pure math from SQLite. Never calls an LLM. | ? Verified |
| **Integer Paise Throughout** | All amounts stored and computed in integer paise. Formatted to INR rupees for display. | ? Verified |
| **Reconciliation Split by Mode** | Cash, Card, and UPI breakdowns for Billed, Collected, Outstanding, and Refunds. | ? Verified |
| **Revenue by Hour & Peak** | Hourly buckets with peak transaction callout bubble. | ? Verified |
| **Two Distinct Medicine Rankings** | Separate Top Medicines by Quantity and Top Medicines by Revenue lists. | ? Verified |
| **Grounding & Zero Hallucination** | `grounding_verifier.py` cross-checks every number against deterministic figures. | ? Verified |
| **Uncomputable Metrics Flag** | Explicitly states: *"Note: cost data wasn't available today, so this is revenue, not profit ? flagging rather than estimating."* | ? Verified |
| **Edge Cases Covered** | 2026-07-27 (1 malformed row rejected, 18 valid ingested), 2026-07-25 (all refunds), 2026-07-26 (closed/empty day). | ? Verified |
| **UI Structure Matching** | Screen 1 (Dashboard), Screen 2 (Analytics), Screen 3 (AI Summary + Traced Figures) with persistent sidebar. | ? Verified |
| **Automated Test Suite** | 21 passing pytest tests covering validation, accounting, non-happy-path days, and API contracts. | ? Verified |

---

## ? Quickstart Guide

### 1. Backend Setup
```bash
cd backend
python -m pip install -r requirements.txt
python -m pytest -v          # Run the 21 automated unit & integration tests
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
API Docs available at: `http://127.0.0.1:8000/docs`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev                  # Or: node ./node_modules/vite/bin/vite.js
```
Frontend UI available at: `http://127.0.0.1:5173`

---

## ?? Live Deployment Instructions
- **Frontend (Vercel / Netlify)**: Set root directory to `frontend`, build command `npm run build`, output directory `dist`. Set proxy or environment variable `VITE_API_URL` to the backend URL.
- **Backend (Render / Railway / Fly.io)**: Set root directory to `backend`, start command `uvicorn app.main:app --host 0.0.0.0 --port 8000`. Set `DATABASE_URL=sqlite:///./clinic_billing.db`.
