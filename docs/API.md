# API.md — Full Endpoint Specification

## UTC Channel Attribution MMM Platform

**Base URL:** `/api/v1`  
**Content-Type:** `application/json`  
**Auth:** Bearer token (set via `API_SECRET_KEY` env var — internal use only)

---

## Endpoint Summary

### Authentication
| Method | Path | Description |
|---|---|---|
| `POST` | `/auth/login` | Authenticate user, receive JWT |
| `POST` | `/auth/logout` | Invalidate token |
| `GET` | `/auth/me` | Get current user info |

### Databricks Metadata (Step 2)
| Method | Path | Description |
|---|---|---|
| `GET` | `/databricks/catalogs` | List available Unity Catalog catalogs |
| `GET` | `/databricks/schemas` | List schemas in a catalog |
| `GET` | `/databricks/tables` | List tables in a schema |
| `POST` | `/databricks/validate-table` | Validate table has expected MMM schema |

### Data Quality (Step 3)
| Method | Path | Description |
|---|---|---|
| `GET` | `/data/report` | Full data quality report for selected table |
| `GET` | `/data/preview` | First N rows of a table |

### Scenarios
| Method | Path | Description |
|---|---|---|
| `POST` | `/scenarios/run` | Create and trigger a new MMM scenario run |
| `GET` | `/scenarios` | List all scenarios (paginated) |
| `GET` | `/scenarios/{scenario_id}` | Get scenario metadata and current status |
| `GET` | `/scenarios/{scenario_id}/status` | Lightweight status poll (for `setInterval`) |
| `GET` | `/scenarios/{scenario_id}/results` | Fetch full attribution results |
| `DELETE` | `/scenarios/{scenario_id}` | Delete a scenario record |

### Comparison & Export
| Method | Path | Description |
|---|---|---|
| `POST` | `/compare` | Fetch multi-scenario data for comparison engine |
| `POST` | `/export/report` | Generate executive PDF/Excel report |

### Health
| Method | Path | Description |
|---|---|---|
| `GET` | `/health` | Health check |

---

## New Endpoints (Steps 1–3 & 9)

---

### POST `/auth/login`

**Request Body**
```json
{ "email": "analyst@utc.com", "password": "..." }
```

**Response — 200 OK**
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 28800,
  "user": { "name": "Jane Smith", "email": "analyst@utc.com", "role": "analyst" }
}
```

---

### GET `/databricks/catalogs`

Returns all catalogs the configured token has access to.

**Response — 200 OK**
```json
{ "catalogs": ["hive_metastore", "unity_catalog", "mmm_dev"] }
```

---

### GET `/databricks/schemas?catalog={catalog}`

**Response — 200 OK**
```json
{ "catalog": "hive_metastore", "schemas": ["utc_attribution", "mmm_prod", "mmm_staging"] }
```

---

### GET `/databricks/tables?catalog={catalog}&schema={schema}`

**Response — 200 OK**
```json
{
  "tables": [
    {
      "name": "mmm_scenario_results",
      "row_count": 377,
      "column_count": 73,
      "last_modified": "2026-04-03T14:05:34Z",
      "partitioned_by": ["run_product", "run_timestamp"],
      "size_bytes": 2400000
    },
    {
      "name": "hcp360_universe",
      "row_count": 13354,
      "column_count": 45,
      "last_modified": "2026-03-01T08:00:00Z",
      "partitioned_by": [],
      "size_bytes": 8900000
    }
  ]
}
```

---

### POST `/databricks/validate-table`

Checks that the selected table has the expected 73-column MMM schema.

**Request Body**
```json
{
  "catalog": "hive_metastore",
  "schema": "utc_attribution",
  "table": "mmm_scenario_results"
}
```

**Response — 200 OK**
```json
{
  "valid": true,
  "column_count": 73,
  "missing_columns": [],
  "extra_columns": [],
  "message": "Table schema matches expected MMM output format."
}
```

**Response — 200 OK (partial mismatch)**
```json
{
  "valid": false,
  "column_count": 68,
  "missing_columns": ["Attribution_Pct_0_2_Years", "no_of_hcp_0_2_Years"],
  "extra_columns": [],
  "message": "5 expected columns are missing. LOB segment columns not found — this table may be from an older model run."
}
```

---

### GET `/data/report?catalog={catalog}&schema={schema}&table={table}`

Full automated data quality report for the selected table.

**Response — 200 OK**
```json
{
  "table": "mmm_scenario_results",
  "generated_at": "2026-04-03T10:30:00Z",
  "overview": {
    "total_rows": 377,
    "unique_scenarios": 12,
    "date_range": { "earliest": "2023-01-01", "latest": "2025-03-31" },
    "completeness_score": 0.84
  },
  "products_present": ["TYVASO", "REMODULIN", "ORENITRAM", "TREPROSTINIL"],
  "attribution_levels_present": ["Touchpoint Level", "Channel Level", "Team Level"],
  "segments_present": ["Cluster Level", "LOB: 0-2 Years vs 2-10 Years vs 10+ Years",
                       "Writes Competitor vs Does Not Writes Competitor (ALL)"],
  "column_report": [
    {
      "column": "Attribution_Pct_High_Performer",
      "data_type": "DOUBLE",
      "non_null_pct": 0.94,
      "null_count": 22,
      "sample_value": 0.3131,
      "status": "complete",
      "note": null
    },
    {
      "column": "Attribution_Pct_All_HCPs",
      "data_type": "STRING",
      "non_null_pct": 0.31,
      "null_count": 260,
      "sample_value": "null",
      "status": "conditional_null",
      "note": "Null when run_segment != 'All HCPs' — expected behaviour"
    }
  ],
  "date_distribution": [
    { "period": "2023-Q1", "scenario_count": 2 },
    { "period": "2023-Q2", "scenario_count": 3 }
  ]
}
```

---

### POST `/export/report`

Generates and streams an executive report PDF or Excel file.

**Request Body**
```json
{
  "report_title": "UTC Channel Attribution — Q4 2025 Analysis",
  "prepared_by": "Jane Smith",
  "confidentiality": "Confidential",
  "scenario_ids": ["uuid-1", "uuid-2"],
  "format": "pdf",
  "page_size": "letter",
  "sections": {
    "executive_summary": true,
    "data_quality_summary": true,
    "scenario_parameters": true,
    "kpi_summary": true,
    "team_donut": true,
    "channel_table": true,
    "segment_heatmap": true,
    "sankey_chart": true,
    "hcp_journey": true,
    "scenario_comparison": true,
    "delta_table": true,
    "raw_data_appendix": false
  }
}
```

**Response — 200 OK**
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="UTC_Attribution_Report_2026-04-03.pdf"
```

---

## Enums

### `AttributionLevel`
```
touchpoint  — Individual interaction types (e.g., MDD_Live_Call, SALES_Virtual_Call)
channel     — Grouped by modality (Live Call, Virtual Call, Email, Speaker Program)
team        — Grouped by team (SALES, MDD, MSL, RNS, SPK PGM, EMAIL)
```

### `HCPSegment`
```
cluster          — Performance cluster (High Performer → Unresponsive)
lob              — Length of Business (0-2 Years, 2-10 Years, 10+ Years)
competitor_drug  — Writes vs. Does Not Write competitor drug
all_hcps         — No segmentation filter (entire HCP universe)
```

### `Product`
```
TYVASO
REMODULIN
ORENITRAM
TREPROSTINIL
ALL
```

### `ScenarioStatus`
```
QUEUED    — Received, Databricks job not yet started
RUNNING   — Databricks job is executing
SUCCESS   — Results written to Delta, ready to fetch
FAILED    — Job failed; see error_message
```

---

## Endpoints

---

### POST `/scenarios/run`

Creates a new MMM scenario run. Triggers a Databricks job asynchronously and returns immediately with a `scenario_id`.

**Request Body**

```json
{
  "scenario_name": "Q4 TYVASO — Cluster Segment",
  "product": "TYVASO",
  "start_date": "2023-01-01",
  "end_date": "2025-03-31",
  "attribution_level": "touchpoint",
  "hcp_segment": "cluster",
  "notes": "Baseline run for Q4 planning"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `scenario_name` | string | Yes | Human-readable label for this run |
| `product` | Product enum | Yes | Product to run attribution for |
| `start_date` | date (YYYY-MM-DD) | Yes | Start of the observation window |
| `end_date` | date (YYYY-MM-DD) | Yes | End of the observation window |
| `attribution_level` | AttributionLevel enum | Yes | Granularity of attribution output |
| `hcp_segment` | HCPSegment enum | Yes | HCP filter to apply |
| `notes` | string | No | Free-text analyst notes |

**Response — 202 Accepted**

```json
{
  "scenario_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "scenario_name": "Q4 TYVASO — Cluster Segment",
  "status": "QUEUED",
  "created_at": "2026-04-03T10:30:00Z",
  "estimated_runtime_seconds": 60,
  "message": "Databricks job queued. Poll /scenarios/{id}/status for updates."
}
```

**Error Responses**

| Code | Reason |
|---|---|
| `422` | Validation error (invalid enum, date format, etc.) |
| `503` | Databricks workspace unreachable |

---

### GET `/scenarios`

Returns a paginated list of all scenario runs, newest first.

**Query Parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `page` | int | 1 | Page number |
| `page_size` | int | 20 | Results per page (max 100) |
| `product` | Product enum | — | Filter by product |
| `status` | ScenarioStatus enum | — | Filter by status |

**Response — 200 OK**

```json
{
  "total": 47,
  "page": 1,
  "page_size": 20,
  "scenarios": [
    {
      "scenario_id": "3fa85f64-...",
      "scenario_name": "Q4 TYVASO — Cluster Segment",
      "product": "TYVASO",
      "attribution_level": "touchpoint",
      "hcp_segment": "cluster",
      "start_date": "2023-01-01",
      "end_date": "2025-03-31",
      "status": "SUCCESS",
      "created_at": "2026-04-03T10:30:00Z",
      "completed_at": "2026-04-03T10:31:42Z",
      "run_timestamp": "2026-04-03T10:31:42Z"
    }
  ]
}
```

---

### GET `/scenarios/{scenario_id}`

Returns full metadata for a single scenario including status and input parameters.

**Response — 200 OK**

```json
{
  "scenario_id": "3fa85f64-...",
  "scenario_name": "Q4 TYVASO — Cluster Segment",
  "product": "TYVASO",
  "start_date": "2023-01-01",
  "end_date": "2025-03-31",
  "attribution_level": "touchpoint",
  "hcp_segment": "cluster",
  "status": "SUCCESS",
  "databricks_run_id": 123456,
  "created_at": "2026-04-03T10:30:00Z",
  "completed_at": "2026-04-03T10:31:42Z",
  "notes": "Baseline run for Q4 planning",
  "error_message": null
}
```

**Error Responses**

| Code | Reason |
|---|---|
| `404` | `scenario_id` not found |

---

### GET `/scenarios/{scenario_id}/status`

**Lightweight polling endpoint.** Called every 5 seconds by `polling.js`. Returns only status and progress — no heavy data.

**Response — 200 OK**

```json
{
  "scenario_id": "3fa85f64-...",
  "status": "RUNNING",
  "progress_pct": 65,
  "message": "Model computing transition matrices...",
  "elapsed_seconds": 38
}
```

Status transitions: `QUEUED` → `RUNNING` → `SUCCESS` | `FAILED`

When `status == "SUCCESS"`, the client should call `/scenarios/{id}/results`.  
When `status == "FAILED"`, the `message` field contains the Databricks error.

---

### GET `/scenarios/{scenario_id}/results`

Returns the full attribution results for a completed scenario. This is the main data source for the KPI dashboard and charts.

**Response — 200 OK**

```json
{
  "scenario_id": "3fa85f64-...",
  "scenario_name": "Q4 TYVASO — Cluster Segment",
  "product": "TYVASO",
  "run_params": {
    "start_date": "2023-01-01",
    "end_date": "2025-03-31",
    "attribution_level": "touchpoint",
    "hcp_segment": "cluster"
  },
  "run_timestamp": "2026-04-03T10:31:42Z",

  "summary_kpis": {
    "total_hcps_in_universe": 1534,
    "total_referrals": 11138,
    "total_touchpoints": 90777,
    "total_prescribers": 2701
  },

  "channel_attribution": [
    {
      "channel": "SALES_Live_Call",
      "team": "SALES",
      "modality": "Live",
      "attribution_pct": {
        "all_hcps": 0.41,
        "high_performer": 0.34,
        "moderate_performer": 0.33,
        "average_performer": 0.27,
        "low_performer": 0.47,
        "near_sleeping": 0.31,
        "sleeping": 0.33,
        "unresponsive": 0.33
      },
      "hcp_counts": {
        "all_hcps": 1209,
        "high_performer": 559,
        "moderate_performer": 226,
        "average_performer": 264,
        "low_performer": 58,
        "near_sleeping": 58,
        "sleeping": 128,
        "unresponsive": 205
      },
      "touchpoint_counts": {
        "all_hcps": 73219,
        "high_performer": 24035,
        "moderate_performer": 9812,
        "average_performer": 11450,
        "low_performer": 2341,
        "near_sleeping": 1984,
        "sleeping": 4201,
        "unresponsive": 8203
      },
      "prescriber_counts": {
        "all_hcps": 2108,
        "high_performer": 490,
        "moderate_performer": 198
      },
      "touchpoints_to_prescribers": {
        "all_hcps": 24035
      }
    }
  ],

  "team_level_summary": {
    "SALES": { "attribution_pct": 0.59, "referrals_attributed": 6571 },
    "MDD":   { "attribution_pct": 0.17, "referrals_attributed": 1893 },
    "MSL":   { "attribution_pct": 0.10, "referrals_attributed": 1114 },
    "RNS":   { "attribution_pct": 0.05, "referrals_attributed": 557  },
    "SPK PGM": { "attribution_pct": 0.05, "referrals_attributed": 557 },
    "EMAIL": { "attribution_pct": 0.03, "referrals_attributed": 334  }
  },

  "competitor_segment_breakdown": {
    "writes_competitor": {
      "SALES": 0.57, "MDD": 0.20, "MSL": 0.12, "RNS": 0.05,
      "SPK_PGM": 0.03, "EMAIL": 0.03
    },
    "does_not_write_competitor": {
      "SALES": 0.64, "MDD": 0.12, "MSL": 0.08, "RNS": 0.05,
      "SPK_PGM": 0.07, "EMAIL": 0.04
    }
  },

  "lob_segment_breakdown": {
    "0_2_years": {
      "SALES": 0.57, "MDD": 0.16, "MSL": 0.10, "RNS": 0.08,
      "SPK_PGM": 0.06, "EMAIL": 0.04
    },
    "2_10_years": {
      "SALES": 0.58, "MDD": 0.21, "MSL": 0.12, "RNS": 0.04,
      "SPK_PGM": 0.02, "EMAIL": 0.03
    },
    "10_plus_years": {
      "SALES": 0.58, "MDD": 0.21, "MSL": 0.12, "RNS": 0.04,
      "SPK_PGM": 0.02, "EMAIL": 0.03
    }
  }
}
```

**Error Responses**

| Code | Reason |
|---|---|
| `404` | `scenario_id` not found |
| `409` | Scenario exists but is not yet in SUCCESS state — poll `/status` first |

---

### DELETE `/scenarios/{scenario_id}`

Soft-deletes a scenario (marks as deleted, retained in Delta for audit).

**Response — 200 OK**

```json
{
  "scenario_id": "3fa85f64-...",
  "deleted": true,
  "message": "Scenario soft-deleted."
}
```

---

### POST `/compare`

Fetches and merges results for 2–4 scenarios to power the comparison engine. Returns a unified dataset aligned by channel.

**Request Body**

```json
{
  "scenario_ids": [
    "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "9bc12e81-2345-6789-abcd-def012345678"
  ],
  "comparison_dimension": "team",
  "hcp_segment_filter": "all_hcps"
}
```

| Field | Type | Required | Description |
|---|---|---|---|
| `scenario_ids` | array[string] | Yes | 2–4 scenario IDs to compare |
| `comparison_dimension` | `team` \| `channel` \| `touchpoint` | No | Override display level (defaults to each scenario's own level) |
| `hcp_segment_filter` | string | No | Pin a specific segment column for comparison (e.g., `"high_performer"`) |

**Response — 200 OK**

```json
{
  "comparison_id": "cmp-abc123",
  "scenarios": [
    {
      "scenario_id": "3fa85f64-...",
      "scenario_name": "Q4 TYVASO — Cluster",
      "product": "TYVASO",
      "attribution_level": "touchpoint",
      "channels": [
        { "channel": "SALES_Live_Call", "attribution_pct": 0.41 },
        { "channel": "MDD_Live_Call",   "attribution_pct": 0.10 }
      ]
    },
    {
      "scenario_id": "9bc12e81-...",
      "scenario_name": "Q4 REMODULIN — Cluster",
      "product": "REMODULIN",
      "attribution_level": "touchpoint",
      "channels": [
        { "channel": "SALES_Live_Call", "attribution_pct": 0.31 },
        { "channel": "MDD_Live_Call",   "attribution_pct": 0.16 }
      ]
    }
  ],
  "delta": [
    {
      "channel": "SALES_Live_Call",
      "scenario_1_pct": 0.41,
      "scenario_2_pct": 0.31,
      "absolute_diff": 0.10,
      "relative_diff_pct": 32.3
    }
  ]
}
```

**Error Responses**

| Code | Reason |
|---|---|
| `400` | Fewer than 2 or more than 4 scenario IDs provided |
| `404` | One or more `scenario_id` values not found |
| `409` | One or more scenarios not yet in SUCCESS state |

---

### GET `/export/{scenario_id}`

Generates and streams a downloadable file.

**Query Parameters**

| Param | Type | Default | Description |
|---|---|---|---|
| `format` | `csv` \| `pdf` | `csv` | Output format |
| `include_segments` | bool | `true` | Include per-segment breakdown columns |

**Response — 200 OK**

For `format=csv`:
```
Content-Type: text/csv
Content-Disposition: attachment; filename="scenario_<id>_results.csv"
```

For `format=pdf`:
```
Content-Type: application/pdf
Content-Disposition: attachment; filename="scenario_<id>_report.pdf"
```

The PDF report includes:
- UTC logo header
- Scenario parameters table
- Team-level attribution donut chart (rendered server-side)
- Channel-level attribution bar table
- Segment breakdown heatmap table
- Footer with run timestamp and scenario ID

---

### GET `/health`

**Response — 200 OK**

```json
{
  "status": "ok",
  "databricks_connection": "ok",
  "delta_table_access": "ok",
  "timestamp": "2026-04-03T10:30:00Z"
}
```

---

## Error Response Schema

All errors follow this structure:

```json
{
  "error": {
    "code": "SCENARIO_NOT_FOUND",
    "message": "No scenario found with id '3fa85f64-...'",
    "details": null,
    "timestamp": "2026-04-03T10:30:00Z"
  }
}
```

## Standard Error Codes

| HTTP Code | Error Code | Description |
|---|---|---|
| 400 | `INVALID_REQUEST` | Malformed request body |
| 404 | `SCENARIO_NOT_FOUND` | Scenario ID does not exist |
| 409 | `SCENARIO_NOT_READY` | Scenario exists but results not yet available |
| 422 | `VALIDATION_ERROR` | Pydantic validation failure |
| 503 | `DATABRICKS_UNAVAILABLE` | Cannot reach Databricks workspace |
| 500 | `INTERNAL_ERROR` | Unexpected server error |
