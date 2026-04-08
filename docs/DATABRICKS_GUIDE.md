# DATABRICKS_GUIDE.md — Notebook, Job & Delta Lake Configuration

## UTC Channel Attribution MMM Platform

---

## 1. Workspace Setup

### Required Resources

| Resource | Type | Purpose |
|---|---|---|
| **MMM Job** | Databricks Job | Runs the attribution model per scenario |
| **SQL Warehouse** | Serverless / Pro | Serves results queries to FastAPI |
| **Delta Tables** | Unity Catalog | Stores all scenario results |

### Environment Variables (FastAPI backend)

```dotenv
DATABRICKS_HOST=https://<your-workspace>.azuredatabricks.net
DATABRICKS_TOKEN=dapi<your-token>
DATABRICKS_JOB_ID=<job_id_from_workspace>
DATABRICKS_SQL_HTTP_PATH=/sql/1.0/warehouses/<warehouse_id>
DATABRICKS_CATALOG=hive_metastore
DATABRICKS_SCHEMA=utc_attribution
DATABRICKS_RESULTS_TABLE=mmm_scenario_results
```

---

## 2. MMM Attribution Notebook (`mmm_attribution.py`)

### Widget Parameters

The notebook accepts these parameters via `dbutils.widgets`. FastAPI passes them as `notebook_params`.

```python
dbutils.widgets.text("scenario_id", "", "Scenario UUID")
dbutils.widgets.text("product", "TYVASO", "Product")
dbutils.widgets.text("start_date", "2023-01-01", "Start Date (YYYY-MM-DD)")
dbutils.widgets.text("end_date", "2025-03-31", "End Date (YYYY-MM-DD)")
dbutils.widgets.text("attribution_level", "touchpoint", "Attribution Level")
dbutils.widgets.text("hcp_segment", "cluster", "HCP Segment")
dbutils.widgets.text("output_table", "utc_attribution.mmm_scenario_results", "Output Table")

# Read params
scenario_id     = dbutils.widgets.get("scenario_id")
product         = dbutils.widgets.get("product")
start_date      = dbutils.widgets.get("start_date")
end_date        = dbutils.widgets.get("end_date")
attr_level      = dbutils.widgets.get("attribution_level")   # touchpoint | channel | team
hcp_segment     = dbutils.widgets.get("hcp_segment")         # cluster | lob | competitor_drug | all_hcps
output_table    = dbutils.widgets.get("output_table")
```

### Notebook Structure

```python
# Cell 1 — Imports and config
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import json
from datetime import datetime

spark = SparkSession.builder.getOrCreate()

# Cell 2 — Load HCP universe (filtered by product + segment)
hcp_df = spark.table("utc_attribution.hcp360_universe")

if product != "ALL":
    hcp_df = hcp_df.filter(col("Segment_Tyvaso").isNotNull() if product == "TYVASO" else ...)

# Cell 3 — Load longitudinal journey (filtered by date range)
journey_df = (
    spark.table("utc_attribution.hcp_longitudinal_journey")
    .filter((col("touchpoint_date") >= start_date) & (col("touchpoint_date") <= end_date))
    .filter(col("product").isin(get_products_for_param(product)))
)

# Cell 4 — Apply attribution level grouping
if attr_level == "team":
    journey_df = journey_df.withColumn("channel_key", col("team"))
elif attr_level == "channel":
    journey_df = journey_df.withColumn("channel_key", col("modality_group"))
else:  # touchpoint
    journey_df = journey_df.withColumn("channel_key", col("channel"))

# Cell 5 — Build Markov transition matrix
# (Uses removal effect method)
transition_df = build_markov_transitions(journey_df)
removal_effects = compute_removal_effects(transition_df)
attribution_df = normalise_attribution(removal_effects)

# Cell 6 — Compute segment breakdowns
# Run attribution separately per segment bucket, then combine
results_by_cluster   = run_for_segment(attribution_df, hcp_df, "cluster")
results_by_lob       = run_for_segment(attribution_df, hcp_df, "lob")
results_by_competitor = run_for_segment(attribution_df, hcp_df, "competitor_drug")

# Cell 7 — Pivot and flatten to 73-column schema
final_df = pivot_to_wide_format(
    results_by_cluster, results_by_lob, results_by_competitor
)

# Cell 8 — Add scenario metadata columns
final_df = final_df.withColumns({
    "scenario_id":   lit(scenario_id),
    "run_product":   lit(product),
    "run_segment":   lit(hcp_segment),
    "run_level":     lit(attr_level),
    "run_start":     lit(start_date).cast("date"),
    "run_end":       lit(end_date).cast("date"),
    "run_timestamp": lit(datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
})

# Cell 9 — Append to Delta table
(
    final_df
    .write
    .format("delta")
    .mode("append")
    .option("mergeSchema", "false")
    .saveAsTable(output_table)
)

print(f"SUCCESS: scenario_id={scenario_id} written to {output_table}")
```

---

## 3. Markov Chain Attribution Logic

### Overview

The model uses the **Removal Effect** method on a first-order Markov chain:

```
1. Build transition probability matrix P[i][j]
   = P(next touchpoint is j | current touchpoint is i)

2. For each channel c, remove it from the transition matrix

3. Re-calculate conversion probability without channel c

4. Removal Effect(c) = (base_conversion_rate - rate_without_c) / base_conversion_rate

5. Normalise all removal effects to sum to 1.0 → this is the attribution %
```

### Memory Decay

An exponential decay weight is applied to touchpoints before building the transition matrix:

```python
# Touchpoints closer to conversion receive higher weight
decay_weight = exp(-lambda * days_before_conversion)
# lambda = 0.05 (configurable — flatter decay for long sales cycles)
```

### Conversion Event

A **conversion** is defined as an HCP writing a new referral for the target product within the observation window. The `hcp_longitudinal_journey` table includes a `conversion` row as the final state for HCPs who converted.

---

## 4. Job Configuration

### Creating the Databricks Job

In the Databricks UI (`Workflows > Jobs > Create Job`):

| Setting | Value |
|---|---|
| Job name | `utc_mmm_attribution` |
| Task type | Notebook |
| Notebook path | `/Repos/utc-attribution/notebooks/mmm_attribution` |
| Cluster type | New job cluster (or existing cluster) |
| Node type | Standard_DS3_v2 (or equivalent) |
| Min workers | 2 |
| Max workers | 8 (autoscaling) |
| Timeout | 600 seconds |
| Max retries | 0 (fail fast) |

Save and note the **Job ID** — this goes in `DATABRICKS_JOB_ID` env var.

### Triggering from FastAPI

```python
# backend/services/databricks_client.py
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunNowRequest
import json, os

w = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    token=os.getenv("DATABRICKS_TOKEN")
)

def trigger_mmm_job(scenario_id: str, params: dict) -> int:
    """
    Triggers the Databricks MMM job with scenario parameters.
    Returns the Databricks run_id.
    """
    run = w.jobs.run_now(
        job_id=int(os.getenv("DATABRICKS_JOB_ID")),
        notebook_params={
            "scenario_id":       scenario_id,
            "product":           params["product"],
            "start_date":        params["start_date"],
            "end_date":          params["end_date"],
            "attribution_level": params["attribution_level"],
            "hcp_segment":       params["hcp_segment"],
            "output_table":      os.getenv("DATABRICKS_RESULTS_TABLE",
                                           "utc_attribution.mmm_scenario_results")
        }
    )
    return run.run_id

def get_job_status(run_id: int) -> dict:
    """
    Returns the current status of a Databricks job run.
    Maps Databricks states to our ScenarioStatus enum.
    """
    run = w.jobs.get_run(run_id=run_id)
    state = run.state

    status_map = {
        "PENDING":    "QUEUED",
        "RUNNING":    "RUNNING",
        "TERMINATING":"RUNNING",
        "TERMINATED": "SUCCESS" if state.result_state.value == "SUCCESS" else "FAILED",
        "SKIPPED":    "FAILED",
        "INTERNAL_ERROR": "FAILED"
    }

    life_state = state.life_cycle_state.value if state.life_cycle_state else "PENDING"
    status = status_map.get(life_state, "QUEUED")

    # Estimate progress from life cycle state
    progress_map = { "QUEUED": 5, "RUNNING": 50, "SUCCESS": 100, "FAILED": 0 }

    return {
        "status": status,
        "progress_pct": progress_map.get(status, 0),
        "message": state.state_message or status,
        "databricks_life_cycle_state": life_state
    }
```

### Querying Results from Delta Lake

```python
# backend/services/databricks_client.py (continued)
from databricks import sql as dbsql

def fetch_scenario_results(scenario_id: str) -> list[dict]:
    """
    Queries Delta Lake for all rows matching this scenario_id.
    Returns a list of row dicts.
    """
    with dbsql.connect(
        server_hostname=os.getenv("DATABRICKS_HOST").replace("https://", ""),
        http_path=os.getenv("DATABRICKS_SQL_HTTP_PATH"),
        access_token=os.getenv("DATABRICKS_TOKEN")
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
                SELECT *
                FROM {os.getenv('DATABRICKS_RESULTS_TABLE',
                                 'utc_attribution.mmm_scenario_results')}
                WHERE scenario_id = ?
                ORDER BY Channel
                """,
                [scenario_id]
            )
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
```

---

## 5. Delta Table DDL

```sql
-- databricks/schemas/delta_tables.sql

-- Main results table (append-only, partitioned for fast scenario lookup)
CREATE TABLE IF NOT EXISTS utc_attribution.mmm_scenario_results (
  scenario_id                                       STRING,
  run_product                                       STRING,
  run_segment                                       STRING,
  run_level                                         STRING,
  run_start                                         DATE,
  run_end                                           DATE,
  run_timestamp                                     TIMESTAMP,
  Product                                           STRING,
  Channel                                           STRING,

  -- Attribution percentages (cluster)
  Attribution_Pct_High_Performer                    DOUBLE,
  Attribution_Pct_Moderate_Performer                DOUBLE,
  Attribution_Pct_Average_Performer                 DOUBLE,
  Attribution_Pct_Low_Performer                     DOUBLE,
  Attribution_Pct_Near_Sleeping                     DOUBLE,
  Attribution_Pct_Sleeping                          DOUBLE,
  Attribution_Pct_Unresponsive                      DOUBLE,
  Attribution_Pct_All_HCPs                          STRING,

  -- Attribution percentages (competitor)
  Attribution_Pct_does_not_writes                   STRING,
  Attribution_Pct_writes                            STRING,

  -- Attribution percentages (LOB)
  Attribution_Pct_0_2_Years                         STRING,
  Attribution_Pct_2_10_Years                        STRING,
  Attribution_Pct_10_plus_Years                     STRING,

  -- HCP counts (cluster)
  no_of_hcp_High_Performer                          BIGINT,
  no_of_hcp_Moderate_Performer                      BIGINT,
  no_of_hcp_Average_Performer                       BIGINT,
  no_of_hcp_Low_Performer                           BIGINT,
  no_of_hcp_Near_Sleeping                           BIGINT,
  no_of_hcp_Sleeping                                BIGINT,
  no_of_hcp_Unresponsive                            BIGINT,
  no_of_hcp_All_HCPs                                STRING,
  no_of_hcp_does_not_writes                         STRING,
  no_of_hcp_writes                                  STRING,
  no_of_hcp_0_2_Years                               STRING,
  no_of_hcp_2_10_Years                              STRING,
  no_of_hcp_10_plus_Years                           STRING,

  -- Touchpoint counts (same 13-column pattern for each metric group)
  total_touchpoints_High_Performer                  BIGINT,
  total_touchpoints_Moderate_Performer              BIGINT,
  total_touchpoints_Average_Performer               BIGINT,
  total_touchpoints_Low_Performer                   BIGINT,
  total_touchpoints_Near_Sleeping                   BIGINT,
  total_touchpoints_Sleeping                        BIGINT,
  total_touchpoints_Unresponsive                    BIGINT,
  total_touchpoints_All_HCPs                        STRING,
  total_touchpoints_does_not_writes                 STRING,
  total_touchpoints_writes                          STRING,
  total_touchpoints_0_2_Years                       STRING,
  total_touchpoints_2_10_Years                      STRING,
  total_touchpoints_10_plus_Years                   STRING,

  -- Prescriber counts
  no_of_prescribers_High_Performer                  BIGINT,
  no_of_prescribers_Moderate_Performer              BIGINT,
  no_of_prescribers_Average_Performer               BIGINT,
  no_of_prescribers_Low_Performer                   BIGINT,
  no_of_prescribers_Near_Sleeping                   BIGINT,
  no_of_prescribers_Sleeping                        BIGINT,
  no_of_prescribers_Unresponsive                    BIGINT,
  no_of_prescribers_All_HCPs                        STRING,
  no_of_prescribers_does_not_writes                 STRING,
  no_of_prescribers_writes                          STRING,
  no_of_prescribers_0_2_Years                       STRING,
  no_of_prescribers_2_10_Years                      STRING,
  no_of_prescribers_10_plus_Years                   STRING,

  -- Touchpoints to prescribers
  total_touchpoints_to_prescribers_High_Performer   BIGINT,
  total_touchpoints_to_prescribers_Moderate_Performer BIGINT,
  total_touchpoints_to_prescribers_Average_Performer BIGINT,
  total_touchpoints_to_prescribers_Low_Performer    BIGINT,
  total_touchpoints_to_prescribers_Near_Sleeping    BIGINT,
  total_touchpoints_to_prescribers_Sleeping         BIGINT,
  total_touchpoints_to_prescribers_Unresponsive     BIGINT,
  total_touchpoints_to_prescribers_All_HCPs         STRING,
  total_touchpoints_to_prescribers_does_not_writes  STRING,
  total_touchpoints_to_prescribers_writes           STRING,
  total_touchpoints_to_prescribers_0_2_Years        STRING,
  total_touchpoints_to_prescribers_2_10_Years       STRING,
  total_touchpoints_to_prescribers_10_plus_Years    STRING
)
USING DELTA
PARTITIONED BY (run_product, run_timestamp)
TBLPROPERTIES (
  'delta.autoOptimize.optimizeWrite' = 'true',
  'delta.autoOptimize.autoCompact' = 'true'
);

-- Scenario inputs / status tracking table
CREATE TABLE IF NOT EXISTS utc_attribution.raw_scenario_inputs (
  scenario_id         STRING NOT NULL,
  scenario_name       STRING,
  product             STRING,
  start_date          DATE,
  end_date            DATE,
  attribution_level   STRING,
  hcp_segment         STRING,
  status              STRING DEFAULT 'QUEUED',
  databricks_run_id   BIGINT,
  created_at          TIMESTAMP DEFAULT current_timestamp(),
  completed_at        TIMESTAMP,
  error_message       STRING,
  notes               STRING,
  is_deleted          BOOLEAN DEFAULT false,
  params_json         STRING
)
USING DELTA
TBLPROPERTIES ('delta.enableChangeDataFeed' = 'true');
```

---

## 6. Cluster Recommendations

| Use Case | Cluster Type | Node Type | Notes |
|---|---|---|---|
| Model execution (per scenario) | Job cluster (autoscaling) | Standard_DS3_v2 × 2–8 | Terminates after job; cost-efficient |
| Results queries | SQL Warehouse (Serverless) | Managed by Databricks | Fast startup ~3s; pay per query |
| Development / testing | Interactive cluster | Standard_DS3_v2 × 1–4 | Keep alive during dev; terminate at EOD |

---

## 7. Monitoring & Alerting

Set up Databricks job alerts:

1. Go to `Workflows > Jobs > utc_mmm_attribution > Alerts`
2. Add email alert on **Job Failed**
3. FastAPI also logs `FAILED` status to `raw_scenario_inputs.error_message`

For the SQL Warehouse, enable **Query History** in the Databricks UI to monitor query latency and catch slow result fetches.
