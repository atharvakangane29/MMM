# ARCHITECTURE.md — System Design

## UTC Channel Attribution MMM Platform

---

## 1. High-Level Architecture

### User Flow (9 Steps)
```
  ①           ②              ③             ④              ⑤
LOGIN  →  DATA SOURCE  →  DATA REPORT  →  CONFIGURE  →  SCHEMA &
                                          SCENARIO       UNIVERSE KPIs
                                                              │
  ⑨           ⑧              ⑦             ⑥              ◄──┘
EXPORT  ←  COMPARISON  ←  SCENARIO    ←  RESULTS
REPORT                    BUILDER        DASHBOARD
```

### Component Architecture
```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              BROWSER (Client)                               │
│                                                                             │
│  ① Login   ② Data     ③ Data    ④ Configure  ⑤ Schema    ⑥ Dashboard     │
│            Source     Report    Scenario     & KPIs      (Sankey +        │
│                                                           HCP Journey)     │
│                                                                             │
│  ⑦ Scenario  ⑧ Comparison   ⑨ Export                                     │
│    Builder     Engine         Report                                        │
│                                                                             │
│  ─────────────────── state.js (Map — persists across all steps) ─────────  │
│                                    │                                        │
│                 stepper.js · polling.js · sankey.js · charts.js            │
│                                    │                                        │
│                               api.js (fetch)                               │
└────────────────────────────────────┼────────────────────────────────────────┘
                                     │ HTTP/REST + JWT Bearer
                                     ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Backend                                  │
│                                                                             │
│  /auth/*          — JWT login, logout, me                                  │
│  /databricks/*    — Catalog/schema/table discovery + validation             │
│  /data/*          — Data quality report, schema, universe KPIs, preview    │
│  /scenarios/*     — Run trigger, status poll, results fetch, clone         │
│  /compare         — Multi-scenario merge engine                             │
│  /export/report   — PDF + Excel executive report generator                  │
│                                                                             │
│  BackgroundTasks (async Databricks job trigger)                             │
│  Pydantic v2 schemas on all inputs/outputs                                  │
└──────────────────────┬──────────────────────────────────────────────────────┘
                       │
          ┌────────────┴──────────────┐
          │                           │
          ▼                           ▼
┌──────────────────┐      ┌───────────────────────┐
│  Databricks      │      │  Databricks           │
│  Jobs API        │      │  SQL Warehouse        │
│  (Trigger MMM    │      │  (Query Delta Lake    │
│   Notebook)      │      │   for all reads)      │
└────────┬─────────┘      └──────────┬────────────┘
         │                           │
         ▼                           ▼
┌──────────────────────────────────────────────────┐
│               Delta Lake (Unity Catalog)         │
│                                                  │
│  utc_attribution.mmm_scenario_results   (output) │
│  utc_attribution.raw_scenario_inputs    (status) │
│  utc_attribution.hcp360_universe        (HCPs)   │
│  utc_attribution.hcp_longitudinal_journey        │
└──────────────────────────────────────────────────┘
```

---

## 2. Request Lifecycle (Detailed)

### Step 1 — Analyst Submits a Scenario

```
Browser
  │
  ├─ User fills Scenario Builder form:
  │    product=TYVASO, start=2023-01-01, end=2025-03-31
  │    attribution_level=touchpoint, hcp_segment=cluster
  │
  └─ api.js calls POST /api/v1/scenarios/run
```

### Step 2 — FastAPI Validates + Triggers Job

```
FastAPI /scenarios/run
  │
  ├─ Pydantic validates request body
  ├─ Generates scenario_id = UUID4
  ├─ Inserts row into Delta `raw_scenario_inputs` (status=QUEUED)
  ├─ Returns 202 { scenario_id, status: "QUEUED" } immediately
  │
  └─ BackgroundTask fires:
       databricks_client.run_mmm_job(scenario_id, params)
         → w.jobs.run_now(job_id=DATABRICKS_JOB_ID, notebook_params={...})
         → saves databricks_run_id to DB
```

### Step 3 — Frontend Polls Status

```
Browser polling.js
  │
  └─ setInterval(5000ms):
       GET /api/v1/scenarios/{id}/status
         ├─ FastAPI calls w.jobs.get_run(run_id)
         ├─ Maps Databricks state → {QUEUED, RUNNING, SUCCESS, FAILED}
         └─ Returns { status, progress_pct, message }

       When status == "SUCCESS":
         → stop polling
         → call GET /api/v1/scenarios/{id}/results
         → render charts
```

### Step 4 — Results Fetched from Delta Lake

```
FastAPI /scenarios/{id}/results
  │
  └─ SQL Connector queries:
       SELECT * FROM utc_attribution.mmm_scenario_results
       WHERE scenario_id = '{id}'
       ORDER BY channel

     Returns structured JSON:
       {
         "summary_kpis": { ... },
         "channel_attribution": [ { channel, attribution_pct, ... } ],
         "segment_breakdown": { ... },
         "metadata": { ... }
       }
```

### Step 5 — Comparison Engine

```
Browser comparison.js
  │
  ├─ User selects 2 scenario IDs from sidebar history
  │
  └─ POST /api/v1/compare { scenario_ids: ["id1", "id2"] }
       → FastAPI fetches both results
       → Merges into side-by-side dataset
       → Returns { scenarios: [{...}, {...}] }
       → charts.js renders dual-bar or overlay charts
```

---

## 3. Async Job Pattern (Why BackgroundTasks, Not WebSockets)

MMM jobs typically run for **30–120 seconds** on Databricks. The chosen pattern is:

- **Immediate 202 response** — no hanging HTTP connections
- **Client-side polling** — simple `setInterval(5000)` in `polling.js`
- **No Redis / message queue** — status is read directly from the Databricks Jobs API via the SDK

This keeps infrastructure minimal. If jobs grow beyond 5 minutes or require push notifications, the pattern can be upgraded to **Server-Sent Events (SSE)** without changing the frontend contract.

---

## 4. Databricks Layer Architecture

### Model: Markov Chain Multi-Touch Attribution

The attribution model is a **first-order Markov chain** with memory decay. It works as follows:

```
HCP Longitudinal Journey Table
  (ordered sequence of marketing touchpoints per HCP)
          │
          ▼
  Transition Matrix Calculation
  (probability of moving from channel A → B → Conversion)
          │
          ▼
  Removal Effect Computation
  (how much does attribution drop if channel X is removed?)
          │
          ▼
  Normalised Attribution %
  (per channel, per HCP segment)
          │
          ▼
  APPEND to mmm_scenario_results Delta Table
  (with scenario_id, run_timestamp, params)
```

### Key Databricks Notebooks

| Notebook | Purpose |
|---|---|
| `mmm_attribution.py` | Main model — reads params via `dbutils.widgets`, runs Markov chain, writes to Delta |
| `hcp360_builder.py` | Builds the HCP360 universe table (run periodically, not per scenario) |
| `longitudinal_journey.py` | Constructs the ordered touchpoint sequences per HCP |

### Job Parameters (passed as `notebook_params`)

```json
{
  "scenario_id": "uuid-...",
  "product": "TYVASO",
  "start_date": "2023-01-01",
  "end_date": "2025-03-31",
  "attribution_level": "touchpoint",
  "hcp_segment": "cluster",
  "output_table": "utc_attribution.mmm_scenario_results"
}
```

---

## 5. Delta Lake Table Architecture

```
hive_metastore / utc_attribution
│
├── mmm_scenario_results          ← Main output table (append-only)
│     Partitioned by: product, run_timestamp
│     Primary key: scenario_id + channel
│
├── raw_scenario_inputs           ← Scenario metadata + status tracking
│     scenario_id, params_json, status, created_at, databricks_run_id
│
├── hcp360_universe               ← HCP master table (periodically refreshed)
│     NPI, segment, LOB, competitor_flag, referral_counts, call_counts
│
└── hcp_longitudinal_journey      ← Ordered touchpoint sequences
      hcp_id, touchpoint_date, touchpoint_type, product, team
```

---

## 6. Frontend Component Architecture

```
index.html
│
├── pages/dashboard.html
│     └── KPI Cards (attribution %, HCPs reached, touchpoints, prescribers)
│         per channel row, per segment column
│
├── pages/scenario-builder.html
│     ├── Product selector (dropdown)
│     ├── Date range pickers
│     ├── Attribution level (radio: touchpoint / channel / team)
│     ├── HCP Segment (radio: cluster / lob / competitor)
│     ├── Run button → api.js → POST /scenarios/run
│     └── Status bar → polling.js → GET /scenarios/{id}/status
│
└── pages/comparison.html
      ├── Scenario sidebar (history list, pin to compare)
      ├── Comparison mode toggle (side-by-side / overlay)
      ├── Split bar chart (ApexCharts)
      ├── Segment heatmap (Chart.js)
      └── Export button → export.js → PDF / CSV
```

### State Management

```javascript
// js/state.js — single source of truth for the frontend
const appState = {
  scenarios: new Map(),         // scenario_id → full result object
  activeScenario: null,         // currently viewed scenario_id
  comparisonSet: [],            // up to 4 scenario_ids for compare view
  pollingTimers: new Map(),     // scenario_id → setInterval reference

  addScenario(id, data) { ... },
  removeScenario(id) { ... },
  pinToCompare(id) { ... },
  unpinFromCompare(id) { ... },
  updateCharts() { ... }        // triggers re-render of all chart instances
};
```

---

## 7. Security Considerations

| Concern | Mitigation |
|---|---|
| Databricks token exposure | Token stored server-side in env vars only; never sent to browser |
| CORS | FastAPI `CORSMiddleware` restricts to `CORS_ORIGINS` env var |
| Input validation | Pydantic v2 enforces strict types and enum values on all endpoints |
| SQL injection | All Delta queries use parameterised SQL via the Databricks SQL Connector |
| Export file size | PDF/CSV generation caps at 10 scenarios per export to prevent memory issues |

---

## 8. Performance Considerations

| Scenario | Approach |
|---|---|
| Job takes > 2 min | UI shows animated progress bar; polling continues silently |
| Multiple concurrent runs | Each run is fully isolated by `scenario_id`; no shared state in FastAPI |
| Large result sets (73 cols × 377 rows) | Backend aggregates to JSON before sending; no raw Delta data in frontend |
| Chart re-renders | Chart.js instances are updated with `.update()`, not destroyed/rebuilt |
| Browser history of runs | `localStorage` caches `scenario_id` list; results fetched on demand from API |
