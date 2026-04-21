# UTC Channel Attribution — MMM Scenario Explorer

> A pharma-grade **Multi-Channel Attribution & Mixed Marketing Model (MMM) scenario comparison platform** built for United Therapeutics' Circulants portfolio. The application allows analysts to run Markov-chain attribution models on Databricks, visualise channel contributions across HCP segments, and compare multiple scenarios side-by-side in a beautiful, exportable dashboard.

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Tech Stack](#2-tech-stack)
3. [Repository Structure](#3-repository-structure)
4. [Quick Start](#4-quick-start)
5. [Core Concepts](#5-core-concepts)
6. [Documents Index](#6-documents-index)
7. [Environment Variables](#7-environment-variables)
8. [Running Locally](#8-running-locally)
9. [Deployment](#9-deployment)

---

## 1. Project Overview

The platform solves a single business problem: **"Given a set of marketing-channel inputs and HCP segment filters, what proportion of referral conversions should be attributed to each channel — and how does that change across scenarios?"**

### What an Analyst Does — 9-Step Flow

1. **Login** — authenticates via email/password or SSO (JWT token issued).
2. **Connect Data Source** — selects Databricks catalog, schema, and results table with live preview.
3. **Data Quality Report** — reviews automated completeness, date coverage, and null analysis before running any model.
4. **Configure Scenario** — names the scenario, sets product, date range, attribution level, and HCP segment. Triggers the Databricks Markov chain job.
5. **Data Schema & Marketing KPIs** — explores the 73-column schema and universe-level KPIs while the model runs in the background.
6. **Results Dashboard** — views KPI cards, team attribution donut, channel table, a Sankey flow diagram (team → channel → segment → conversion), and an HCP vertical movement / journey chart.
7. **Scenario Builder** — creates additional scenarios (clone and modify), monitors run status, pins scenarios for comparison.
8. **Scenario Comparison** — side-by-side grouped bars, overlay charts, waterfall chart, delta table, and auto-generated insight summary.
9. **Export Executive Report** — builds a customisable PDF/Excel report with cover page, KPIs, charts, comparison, and data appendix.

### Products Supported

| Product | Brand | Disease Area |
|---|---|---|
| TYVASO | Tyvaso (inhaled treprostinil) | PAH / PH-ILD |
| REMODULIN | Remodulin (IV/SC treprostinil) | PAH |
| ORENITRAM | Orenitram (oral treprostinil) | PAH |
| TREPROSTINIL | All treprostinil forms combined | PAH / PH-ILD |
| ALL | All products combined | — |

### Channels in the Model

`SALES Live Call · SALES Virtual Call · MDD Live Call · MDD Phone/Email · MDD Virtual · MSL Live Call · MSL Virtual · MSL Conference · MSL Phone · RNS Live · RNS Virtual · RNS Phone · Speaker Program Live · Speaker Program Virtual · Email Clicked`

---

## 2. Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **Frontend** | Vanilla JS + Tailwind CSS | Scenario forms, charts, export |
| **Charting** | ApexCharts / Chart.js | Bar, waterfall, heatmap, area charts |
| **Export** | jsPDF + SheetJS | PDF and CSV scenario reports |
| **Backend** | FastAPI (Python 3.11+) | REST API, job orchestration, data gateway |
| **Async Jobs** | FastAPI `BackgroundTasks` | Non-blocking Databricks job trigger |
| **Compute** | Databricks (Jobs API) | Markov chain MMM model execution |
| **Storage** | Databricks Delta Lake | Scenario results, HCP360 universe |
| **SDK** | `databricks-sdk` Python | Job trigger + SQL connector |
| **Validation** | Pydantic v2 | Request / response schema enforcement |

---

## 3. Repository Structure

```
utc-attribution-app/
├── backend/
│   ├── main.py                  # FastAPI app entry point
│   ├── routers/
│   │   ├── auth.py              # /auth/login, /auth/logout, token validation
│   │   ├── databricks_meta.py   # /databricks/catalogs, /schemas, /tables, /validate-table
│   │   ├── data_report.py       # /data/report — completeness, date coverage, nulls
│   │   ├── scenarios.py         # /scenarios CRUD + run trigger
│   │   ├── results.py           # /results fetch + aggregation
│   │   ├── compare.py           # /compare multi-scenario engine
│   │   └── export.py            # /export/report — PDF + Excel generation
│   ├── services/
│   │   ├── databricks_client.py # Job trigger + SQL connector
│   │   ├── data_quality.py      # Completeness and null analysis logic
│   │   └── polling.py           # Job status checker
│   ├── schemas/
│   │   ├── auth.py              # Pydantic auth models
│   │   ├── scenario.py          # Pydantic input/output models
│   │   └── results.py           # Pydantic result models
│   └── config.py                # Env vars, Databricks workspace config
├── frontend/
│   ├── index.html               # App shell + router
│   ├── pages/
│   │   ├── login.html           # Step 1 — Authentication
│   │   ├── data-source.html     # Step 2 — DB/Table selection
│   │   ├── data-report.html     # Step 3 — Data quality report
│   │   ├── configure.html       # Step 4 — Hyperparameter config + scenario name
│   │   ├── schema.html          # Step 5 — Data schema + marketing KPIs
│   │   ├── dashboard.html       # Step 6 — KPI + Sankey + HCP Journey
│   │   ├── scenario-builder.html# Step 7 — Multi-scenario management
│   │   ├── comparison.html      # Step 8 — Scenario comparison engine
│   │   └── export.html          # Step 9 — Executive report export
│   ├── js/
│   │   ├── state.js             # Global app state (Map-based, persists across steps)
│   │   ├── api.js               # fetch() wrappers for all endpoints
│   │   ├── auth.js              # Login, token management
│   │   ├── stepper.js           # Progress stepper navigation logic
│   │   ├── charts.js            # ApexCharts/D3 renderers (donut, bar, heatmap)
│   │   ├── sankey.js            # D3-based Sankey + HCP journey chart
│   │   ├── comparison.js        # Comparison engine logic
│   │   ├── export.js            # Report builder options + download trigger
│   │   └── polling.js           # Status poller (setInterval)
│   └── css/
│       └── custom.css           # CSS custom properties (palette) + component styles
├── databricks/
│   ├── notebooks/
│   │   └── mmm_attribution.py   # Markov chain model notebook
│   └── schemas/
│       └── delta_tables.sql     # Delta Lake DDL
├── docs/
│   ├── README.md                # ← This file
│   ├── USER_FLOW.md             # ★ Canonical 9-step user journey (start here)
│   ├── ARCHITECTURE.md          # System design + data flow
│   ├── API.md                   # All API endpoints (full spec)
│   ├── DATA_SCHEMA.md           # Delta table schemas + column glossary
│   ├── FRONTEND_GUIDE.md        # Component map, state management, chart specs
│   └── DATABRICKS_GUIDE.md      # Notebook params, cluster config, job setup
├── .env.example
├── requirements.txt
└── docker-compose.yml
```

---

## 4. Quick Start

```bash
# 1. Clone and install
git clone https://github.com/utc/attribution-app
cd attribution-app
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Fill in DATABRICKS_HOST, DATABRICKS_TOKEN, DATABRICKS_JOB_ID, etc.

# 3. Run FastAPI server
uvicorn backend.main:app --reload --port 8000

# 4. Open frontend
open frontend/index.html
# or serve statically:
python -m http.server 3000 --directory frontend/
```

---

## 5. Core Concepts

### Attribution Level
Controls the granularity of the Markov chain model:
- **Touchpoint Level** — each unique interaction type (e.g., `MDD_Live_Call`, `SALES_Virtual_Call`)
- **Channel Level** — grouped by modality (e.g., `Live Call`, `Virtual Call`, `Email`)
- **Team Level** — grouped by sales team (e.g., `SALES`, `MDD`, `MSL`, `RNS`, `SPK PGM`)

### HCP Segment
Filters the HCP universe before running attribution:
- **Cluster** — segmentation by prescribing performance: `High Performer`, `Moderate Performer`, `Average Performer`, `Low Performer`, `Near Sleeping`, `Sleeping`, `Unresponsive`
- **Length of Business (LOB)** — time since first referral: `0–2 Years`, `2–10 Years`, `10+ Years`
- **Competitor Drug** — whether the HCP also writes for `Yutrepia`, `Uptravi`, or `Winrevair`: `Writes Competitor` vs `Does Not Write Competitor`

### Scenario Run Parameters

| Parameter | Type | Options |
|---|---|---|
| `product` | string | TYVASO, REMODULIN, ORENITRAM, TREPROSTINIL, ALL |
| `start_date` | date | Any date (model trained on 2023-01-01 → 2025-03-31 baseline) |
| `end_date` | date | Any date after `start_date` |
| `attribution_level` | enum | `touchpoint`, `channel`, `team` |
| `hcp_segment` | enum | `cluster`, `lob`, `competitor_drug` |

### Result Table Structure
Results are **appended** to a single Delta table (one row per channel per scenario), identifiable by `run_timestamp` and `scenario_id`. See `DATA_SCHEMA.md` for full column glossary.

---

## 6. Documents Index

| Document | What it covers |
|---|---|
| `USER_FLOW.md` | ★ **Start here** — canonical 9-step user journey, every screen, state, and decision point |
| `ARCHITECTURE.md` | End-to-end data flow, component diagram, async job pattern, polling design |
| `API.md` | Every FastAPI endpoint — method, path, request body, response schema, error codes |
| `DATA_SCHEMA.md` | All 73 Delta Lake columns explained with data types and business definitions |
| `FRONTEND_GUIDE.md` | Page-by-page component map, JS state manager, chart specs (incl. Sankey + HCP Journey) |
| `DATABRICKS_GUIDE.md` | Notebook parameterisation, job cluster config, widget inputs, Delta write patterns |

---

## 7. Environment Variables

```dotenv
# Databricks
DATABRICKS_HOST=https://<workspace>.azuredatabricks.net
DATABRICKS_TOKEN=dapi...
DATABRICKS_JOB_ID=987654321
DATABRICKS_SQL_HTTP_PATH=/sql/1.0/warehouses/<warehouse_id>
DATABRICKS_CATALOG=hive_metastore
DATABRICKS_SCHEMA=utc_attribution
DATABRICKS_RESULTS_TABLE=mmm_scenario_results

# FastAPI
APP_ENV=development
API_SECRET_KEY=<random_string>
CORS_ORIGINS=http://localhost:3000

# Export
PDF_LOGO_PATH=./frontend/assets/utc_logo.png
```

---

## 8. Running Locally

The frontend is **pure static HTML/JS/CSS** — no build step required. Serve it with any static file server. The FastAPI backend connects to your Databricks workspace via the SDK.

For local development without a live Databricks connection, use the **mock mode**:
```bash
APP_ENV=mock uvicorn backend.main:app --reload
```
Mock mode returns pre-seeded scenario results from the `Result.xlsx` baseline dataset.

---

## 9. Deployment

- **Backend**: Docker container on Azure App Service or AWS ECS. See `docker-compose.yml`.
- **Frontend**: Azure Static Web Apps or S3 + CloudFront (zero build config needed).
- **Databricks**: Existing workspace — only a Job ID and SQL Warehouse HTTP path required.

The architecture is intentionally **thin on infrastructure** — no message queue, no Redis, no websockets. Status polling uses standard HTTP long-polling via `setInterval` in the browser.
