Here are the corrected and updated versions of both documentation files.

### 1\. Corrected `DATA_SCHEMA.md`

````markdown
# DATA_SCHEMA.md — Delta Lake Tables & Column Glossary

## UTC Channel Attribution MMM Platform

All tables live in the Databricks Unity Catalog under:
```text
Catalog: coe-consultant-catalog
Schemas: results (Master Table)
         channel_attribution (Longitudinal & Journey Tables)
````

-----

## Table Index

| Table | Description |
|---|---|
| `results.channel_attribution_master_test` | Primary output table — one row per channel per segment run |
| `channel_attribution.hcp_longitudinal_data_test` | Ordered touchpoint sequence per HCP with generated journey IDs |
| `channel_attribution.hcp_journeys_test` | Aggregated journey paths (arrays) per journey ID |

*(Note: The HCP Universe is built dynamically at runtime by joining Veeva, Tableau, and Competitor datasets. There is no static `hcp360_universe` table.)*

-----

## Table 1: `channel_attribution_master_test`

The **central output table**. Every scenario run appends rows here. The frontend or BI tools read this table exclusively for chart rendering.

### Scenario Identity Columns

| Column | Type | Example | Description |
|---|---|---|---|
| `run_product` | STRING | `REMODULIN` | Product parameter used for this run (can be comma-separated if ALL is selected) |
| `run_segment` | STRING | `Cluster Level` | HCP segment filter mapped from input (e.g., "Cluster Level", "All HCPs") |
| `run_level` | STRING | `Touchpoint Level` | Attribution granularity used |
| `run_start` | DATE | `2023-01-01` | Observation window start |
| `run_end` | DATE | `2025-03-31` | Observation window end |
| `run_timestamp` | STRING | `2026-01-17 14:05:34` | When the model output was saved |

### Channel Identity Columns

| Column | Type | Example | Description |
|---|---|---|---|
| `Product` | STRING | `REMODULIN` | Product being attributed |
| `Channel` | STRING | `SALES_Live_Call` | The marketing channel / touchpoint / team being described |

### Attribution Percentage Columns

Each value is a `DOUBLE` (0.0–1.0) representing the Markov-chain attribution share for that channel within that segment.

| Column | Segment Description |
|---|---|
| `Attribution_Pct_High_Performer` | HCPs in the "High Performer" prescribing cluster |
| `Attribution_Pct_Moderate_Performer` | HCPs in the "Moderate Performer" cluster |
| `Attribution_Pct_Average_Performer` | HCPs in the "Average Performer" cluster |
| `Attribution_Pct_Low_Performer` | HCPs in the "Low Performer" cluster |
| `Attribution_Pct_Near_Sleeping` | HCPs with low recent engagement |
| `Attribution_Pct_Sleeping` | HCPs with very low recent engagement |
| `Attribution_Pct_Unresponsive` | HCPs with near-zero engagement |
| `Attribution_Pct_All_HCPs` | Entire HCP universe (no segment filter) |
| `Attribution_Pct_does_not_writes` | HCPs who do NOT prescribe competitor drugs |
| `Attribution_Pct_writes` | HCPs who DO prescribe competitor drugs |
| `Attribution_Pct_0_2_Years` | HCPs with 0–2 years since first referral |
| `Attribution_Pct_2_10_Years` | HCPs with 2–10 years since first referral |
| `Attribution_Pct_10_plus_Years` | HCPs with 10+ years since first referral |

### HCP Count Columns (BIGINT)

*Prefix: `no_of_hcp_`* (e.g., `no_of_hcp_High_Performer`, `no_of_hcp_All_HCPs`).
Counts the number of unique HCPs reached by this channel for the given segment.

### Total Touchpoints Columns (BIGINT)

*Prefix: `total_touchpoints_`*
Counts the total volume of individual touchpoint events delivered by this channel to HCPs in each segment.

### Prescriber Count Columns (BIGINT)

*Prefix: `no_of_prescribers_`*
Counts only the HCPs in each segment who **actually wrote a referral** (i.e., converted).

### Touchpoints-to-Prescribers Columns (BIGINT)

*Prefix: `total_touchpoints_to_prescribers_`*
Touchpoint volume delivered specifically to HCPs who eventually converted. This is an **efficiency signal**.

-----

## Table 2: `hcp_longitudinal_data_test`

Ordered sequence of all marketing touchpoints per HCP over time, merged with their respective journey ID after cutoff rules are applied.

| Column | Type | Description |
|---|---|---|
| `serial_no` | INTEGER | Ordered index of the event |
| `event_id` | STRING | Source ID of the touchpoint/referral |
| `hcp_id` | STRING | Account ID of the HCP |
| `event_channel` | STRING | Broad channel (Call, Email, Referral, Speaker Program) |
| `event_type` | STRING | Modality (Live, Virtual, Clicked, etc.) |
| `event_date` | DATE | Date of interaction |
| `team` | STRING | Team responsible (MDD, MSL, SALES, RNS) |
| `det_touchpoint` | STRING | Most granular level (e.g., `MDD_Live_Call`) |
| `channel_5` | STRING | Mid-level channel aggregation |
| `channel_6` | STRING | Team-level aggregation |
| `journey_id` | STRING | Unique ID linking the event to a specific Markov sequence |

-----

## Table 3: `hcp_journeys_test`

Contains the collapsed journey paths used directly in the Markov transition matrix calculations.

| Column | Type | Description |
|---|---|---|
| `journey_id` | STRING | Unique identifier for a continuous touchpoint sequence |
| `journey_path` | ARRAY\<STRING\> | Ordered list of channels, starting with "Start" and ending with "Conversion" or "Null" |
| `run_product` | STRING | Run context |
| `run_start_date` | DATE | Run context |
| `run_end_date` | DATE | Run context |

````

***

### 2. Corrected `DATABRICKS_GUIDE.md`

```markdown
# DATABRICKS_GUIDE.md — Notebook, Job & Delta Lake Configuration

## UTC Channel Attribution MMM Platform

---

## 1. Workspace Setup

### Required Resources

| Resource | Type | Purpose |
|---|---|---|
| **Data Extraction Tasks** | Databricks Notebooks | Extracts columns and aligns datatypes (`Table Column Filtering.ipynb`, `Column DataType Change.ipynb`) |
| **Orchestrator** | Databricks Notebook | Identifies competitor logic and passes task values (`orchestrator.ipynb`) |
| **MMM Script** | Databricks Python Script | Runs the core data prep and Markov calculations (`main.py`) |
| **Delta Tables** | Unity Catalog | Stores all pipeline outputs in `coe-consultant-catalog` |

---

## 2. MMM Attribution Execution (`main.py`)

Unlike traditional notebook widgets, the core model is a modular Python package triggered via `argparse`. 

### Input Parameters (`_01_input.py`)

The pipeline parses the following command-line arguments passed from the Databricks Job parameters:

```python
parser.add_argument("--start_date", required=True)
parser.add_argument("--end_date", required=True)
parser.add_argument("--product", required=False, default="TREPROSTINIL")
parser.add_argument("--level", required=True)
parser.add_argument("--segment", required=True)
````

**Valid Arguments:**

  * `--product`: `TYVASO`, `REMODULIN`, `ORENITRAM`, `TREPROSTINIL`, or `ALL`.
  * `--level`: `touchpoint level`, `channel level`, `team level`.
  * `--segment`: `1` (All), `2` (Clusters), `3` (LOB), `4` (Direct Competitors), `5` (All Competitors).

### Orchestrator Notebook (`orchestrator.ipynb`)

If `--segment` is `4` or `5`, the `orchestrator.ipynb` notebook resolves the competitor NPI data table and passes it as a task value to `main.py`.

```python
# From orchestrator.ipynb
dbutils.jobs.taskValues.set(key="comp_table", value="`coe-consultant-catalog`.dw.uc_veeva_custom_claims")
# Or None if not a competitor scenario
```

`main.py` fetches this value upon initialization to know whether to join competitor schemas.

-----

## 3\. Markov Chain Attribution Logic

### Overview

The model uses the **Removal Effect** method on a first-order Markov chain:

1.  Build a transition probability matrix `P[i][j]` showing the likelihood of moving from one channel to the next, ending in `Conversion` or `Null`.
2.  For each channel `c`, calculate the global conversion rate.
3.  Remove channel `c` from the matrix and calculate the *new* theoretical conversion rate.
4.  `Removal Effect(c) = 1.0 - (new_conversion_rate / base_conversion_rate)`
5.  Normalize all removal effects to sum to 1.0 (100%). This is the final attribution percentage.

-----

## 4\. Job Configuration

In the Databricks UI (`Workflows > Jobs > Create Job`), sequence the tasks as follows:

1.  **Task 1 (`column_filter`):** Notebook task pointing to `Table Column Filtering.ipynb`.
2.  **Task 2 (`datatype_conversion`):** Notebook task pointing to `Column DataType Change.ipynb`.
3.  **Task 3 (`claims_notebook`):** Notebook task pointing to `orchestrator.ipynb`.
4.  **Task 4 (`main_code`):** Python Script task pointing to `main.py`.

### Passing Parameters to Python Task

You must configure the parameters for the Python script task explicitly using JSON array templating in the Job UI:

```json
["--start_date","{{job.parameters.start_date}}",
 "--end_date","{{job.parameters.end_date}}",
 "--product","{{job.parameters.product}}",
 "--level","{{job.parameters.level}}",
 "--segment","{{job.parameters.segment}}"]
```

-----

## 5\. Master Table DDL

This table is automatically created by `_04_reporting.py` if it does not exist. It utilizes `SCHEMA MERGE` to dynamically capture missing columns.

```sql
CREATE TABLE IF NOT EXISTS `coe-consultant-catalog`.results.channel_attribution_master_test (
    run_product STRING,
    run_segment STRING,
    run_level STRING,
    run_start DATE,
    run_end DATE,
    run_timestamp STRING,
    Product STRING,
    Channel STRING,

    -- Attribution % (DOUBLE)
    Attribution_Pct_High_Performer DOUBLE,
    Attribution_Pct_Moderate_Performer DOUBLE,
    Attribution_Pct_Average_Performer DOUBLE,
    Attribution_Pct_Low_Performer DOUBLE,
    Attribution_Pct_Near_Sleeping DOUBLE,
    Attribution_Pct_Sleeping DOUBLE,
    Attribution_Pct_Unresponsive DOUBLE,
    Attribution_Pct_All_HCPs DOUBLE,
    Attribution_Pct_does_not_writes DOUBLE,
    Attribution_Pct_writes DOUBLE,
    Attribution_Pct_0_2_Years DOUBLE,
    Attribution_Pct_2_10_Years DOUBLE,
    Attribution_Pct_10_plus_Years DOUBLE,

    -- HCP Counts (BIGINT)
    no_of_hcp_High_Performer BIGINT,
    no_of_hcp_Moderate_Performer BIGINT,
    no_of_hcp_Average_Performer BIGINT,
    no_of_hcp_Low_Performer BIGINT,
    no_of_hcp_Near_Sleeping BIGINT,
    no_of_hcp_Sleeping BIGINT,
    no_of_hcp_Unresponsive BIGINT,
    no_of_hcp_All_HCPs BIGINT,
    no_of_hcp_does_not_writes BIGINT,
    no_of_hcp_writes BIGINT,
    no_of_hcp_0_2_Years BIGINT,
    no_of_hcp_2_10_Years BIGINT,
    no_of_hcp_10_plus_Years BIGINT,

    -- Total Touchpoints (BIGINT)
    total_touchpoints_High_Performer BIGINT,
    -- [... follows same pattern for all segments ...]
    total_touchpoints_10_plus_Years BIGINT,

    -- Prescribers (BIGINT)
    no_of_prescribers_High_Performer BIGINT,
    -- [... follows same pattern for all segments ...]
    no_of_prescribers_10_plus_Years BIGINT,

    -- Touchpoints to Prescribers (BIGINT)
    total_touchpoints_to_prescribers_High_Performer BIGINT,
    -- [... follows same pattern for all segments ...]
    total_touchpoints_to_prescribers_10_plus_Years BIGINT
)
USING DELTA
```

```
```