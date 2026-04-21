# backend/services/databricks_client.py
"""
All Databricks interaction lives here:
  - SQL Warehouse queries (Databricks SQL Connector)
  - Jobs API calls (databricks-sdk)

Nothing in this file is hardcoded — every credential comes through
the Settings object from config.py.
"""
from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional

from databricks import sql as databricks_sql
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.jobs import RunLifeCycleState, RunResultState

from config import Settings

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Low-level helpers
# ─────────────────────────────────────────────────────────────────────────────

def _get_sdk_client(settings: Settings) -> WorkspaceClient:
    """Return a databricks-sdk WorkspaceClient configured from env vars."""
    return WorkspaceClient(
        host=settings.databricks_host,
        token=settings.databricks_token,
    )


def _sql_connect(settings: Settings):
    """Open a Databricks SQL Warehouse connection with SSL config."""
    # Note: If you have persistent SSL issues, you can pass ssl_verify_cert=False (not recommended for prod)
    return databricks_sql.connect(
        server_hostname=settings.databricks_host.replace("https://", "").split('/')[0],
        http_path=settings.databricks_http_path,
        access_token=settings.databricks_token,
        # session_configuration={"ansi_mode": "true"}
    )



def _run_query(settings: Settings, query: str, params: Optional[tuple] = None) -> List[Dict[str, Any]]:
    """Execute a SQL query and return a list of row dicts."""
    with _sql_connect(settings) as conn:
        with conn.cursor() as cursor:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]


# ─────────────────────────────────────────────────────────────────────────────
# Catalog / Schema / Table Discovery
# ─────────────────────────────────────────────────────────────────────────────

def list_catalogs(settings: Settings) -> List[str]:
    rows = _run_query(settings, "SHOW CATALOGS")
    return [r["catalog"] for r in rows]


def list_schemas(settings: Settings, catalog: str) -> List[str]:
    rows = _run_query(settings, f"SHOW SCHEMAS IN `{catalog}`")
    return [r["databaseName"] for r in rows]


def list_tables(settings: Settings, catalog: str, schema: str) -> List[Dict[str, Any]]:
    rows = _run_query(settings, f"SHOW TABLES IN `{catalog}`.`{schema}`")
    result = []
    for r in rows:
        table_name = r.get("tableName", "")
        # Fetch basic stats for each table
        try:
            stats = _run_query(
                settings,
                f"DESCRIBE DETAIL `{catalog}`.`{schema}`.`{table_name}`",
            )
            s = stats[0] if stats else {}
            result.append({
                "name": table_name,
                "row_count": s.get("numRows") or 0,
                "column_count": _count_columns(settings, catalog, schema, table_name),
                "last_modified": str(s.get("lastModified") or ""),
                "size_bytes": s.get("sizeInBytes") or 0,
            })
        except Exception:
            result.append({"name": table_name, "row_count": None, "column_count": None, "last_modified": None, "size_bytes": None})
    return result


def _count_columns(settings: Settings, catalog: str, schema: str, table: str) -> int:
    rows = _run_query(settings, f"DESCRIBE TABLE `{catalog}`.`{schema}`.`{table}`")
    # DESCRIBE returns col_name, data_type, comment. Filter out partition headers.
    return sum(1 for r in rows if r.get("col_name") and not r["col_name"].startswith("#"))


EXPECTED_COLUMNS = {
    "Attribution_Pct_High_Performer", "Attribution_Pct_Moderate_Performer",
    "Attribution_Pct_Average_Performer", "Attribution_Pct_Low_Performer",
    "Attribution_Pct_Near_Sleeping", "Attribution_Pct_Sleeping",
    "Attribution_Pct_Unresponsive", "Attribution_Pct_All_HCPs",
    "Attribution_Pct_does_not_writes", "Attribution_Pct_writes",
    "Attribution_Pct_0_2_Years", "Attribution_Pct_2_10_Years",
    "Attribution_Pct_10_plus_Years",
    "run_product", "run_segment", "run_level", "run_start", "run_end", "run_timestamp",
    "Product", "Channel",
}


def validate_table(settings: Settings, catalog: str, schema: str, table: str) -> Dict[str, Any]:
    rows = _run_query(settings, f"DESCRIBE TABLE `{catalog}`.`{schema}`.`{table}`")
    actual_cols = {r["col_name"] for r in rows if r.get("col_name") and not r["col_name"].startswith("#")}
    missing = list(EXPECTED_COLUMNS - actual_cols)
    extra = list(actual_cols - EXPECTED_COLUMNS)
    valid = len(missing) == 0
    return {
        "valid": valid,
        "column_count": len(actual_cols),
        "missing_columns": missing,
        "extra_columns": extra,
        "message": (
            "Table schema matches expected MMM output format."
            if valid
            else f"{len(missing)} expected columns are missing — this table may be from an older model run."
        ),
    }


# ─────────────────────────────────────────────────────────────────────────────
# Data Quality Report
# ─────────────────────────────────────────────────────────────────────────────

def get_data_report(settings: Settings, catalog: str, schema: str, table: str) -> Dict[str, Any]:
    """Generate a full data quality report by querying the Delta table."""
    from datetime import datetime

    fqt = f"`{catalog}`.`{schema}`.`{table}`"

    # Overview stats
    overview_rows = _run_query(settings, f"""
        SELECT
            COUNT(*) AS total_rows,
            COUNT(DISTINCT run_segment) AS unique_scenarios,
            MIN(run_start) AS earliest,
            MAX(run_end)  AS latest
        FROM {fqt}
    """)
    ov = overview_rows[0] if overview_rows else {}

    # Column describe
    desc_rows = _run_query(settings, f"DESCRIBE TABLE {fqt}")
    col_names = [r["col_name"] for r in desc_rows if r.get("col_name") and not r["col_name"].startswith("#")]

    # Sample row to build null analysis
    sample_rows = _run_query(settings, f"SELECT * FROM {fqt} LIMIT 1000")
    import pandas as pd
    if sample_rows:
        df = pd.DataFrame(sample_rows)
        null_rates = {c: round(df[c].isna().mean() * 100, 1) for c in df.columns}
    else:
        null_rates = {c: 100.0 for c in col_names}

    # Build column report
    def _group(col: str) -> str:
        if col.startswith("Attribution_Pct_"): return "Attribution %"
        if col.startswith("no_of_hcp_"): return "HCP Counts"
        if col.startswith("total_touchpoints_to_"): return "Prescribers"
        if col.startswith("total_touchpoints_"): return "Touchpoints"
        if col.startswith("no_of_prescribers_"): return "Prescribers"
        return "Run Config"

    def _status(null_rate: float) -> str:
        if null_rate == 0: return "clean"
        if null_rate < 60: return "partial"
        return "missing"

    column_report = [
        {
            "column": c,
            "group": _group(c),
            "data_type": next((r["data_type"] for r in desc_rows if r.get("col_name") == c), "UNKNOWN"),
            "non_null_pct": round(100 - null_rates.get(c, 0), 1),
            "null_rate": null_rates.get(c, 0.0),
            "status": _status(null_rates.get(c, 0.0)),
        }
        for c in col_names
    ]

    # Date distribution
    date_rows = _run_query(settings, f"""
        SELECT DATE_FORMAT(run_start, 'yyyy-QQ') AS period, COUNT(*) AS scenario_count
        FROM {fqt}
        GROUP BY period
        ORDER BY period
    """)

    total_rows = int(ov.get("total_rows") or 0)
    non_null_avg = (sum(r["non_null_pct"] for r in column_report) / len(column_report)) if column_report else 0

    return {
        "table": table,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "overview": {
            "total_rows": total_rows,
            "unique_scenarios": int(ov.get("unique_scenarios") or 0),
            "date_range": {"earliest": str(ov.get("earliest") or ""), "latest": str(ov.get("latest") or "")},
            "completeness_score": round(non_null_avg / 100, 2),
        },
        "column_report": column_report,
        "date_distribution": date_rows,
    }


def get_table_preview(settings: Settings, catalog: str, schema: str, table: str, limit: int = 5) -> List[Dict[str, Any]]:
    return _run_query(settings, f"SELECT * FROM `{catalog}`.`{schema}`.`{table}` LIMIT {limit}")


# ─────────────────────────────────────────────────────────────────────────────
# Scenario Results — read from Delta master table
# ─────────────────────────────────────────────────────────────────────────────

def get_scenario_results_from_delta(settings: Settings, scenario_id: str) -> Optional[Dict[str, Any]]:
    """
    Read the master table rows for a specific scenario_id and transform
    them into the structured JSON format the frontend expects.
    """
    fqt = settings.full_master_table
    rows = _run_query(
        settings,
        f"SELECT * FROM {fqt} WHERE scenario_id = ? ORDER BY Channel",
        (scenario_id,),
    )
    if not rows:
        return None

    first = rows[0]

    # ── Summary KPIs ───────────────────────────────────────────────
    total_hcps = sum(r.get("no_of_hcp_All_HCPs") or 0 for r in rows)
    total_referrals = sum(r.get("no_of_prescribers_All_HCPs") or 0 for r in rows)
    total_touchpoints = sum(r.get("total_touchpoints_All_HCPs") or 0 for r in rows)
    total_prescribers = sum(r.get("no_of_prescribers_All_HCPs") or 0 for r in rows)

    # ── Channel Attribution ─────────────────────────────────────────
    seg_cols = [
        "High_Performer", "Moderate_Performer", "Average_Performer",
        "Low_Performer", "Near_Sleeping", "Sleeping", "Unresponsive",
        "All_HCPs", "does_not_writes", "writes",
        "0_2_Years", "2_10_Years", "10_plus_Years",
    ]

    channel_attribution = []
    for r in rows:
        channel = r.get("Channel", "")
        # derive team from channel name (e.g. SALES_Live_Call → SALES)
        team = channel.split("_")[0] if "_" in channel else channel

        attr_pct = {}
        hcp_counts = {}
        tp_counts = {}
        for seg in seg_cols:
            attr_pct[seg.lower()] = r.get(f"Attribution_Pct_{seg}")
            hcp_counts[seg.lower()] = r.get(f"no_of_hcp_{seg}")
            tp_counts[seg.lower()] = r.get(f"total_touchpoints_{seg}")

        channel_attribution.append({
            "channel": channel,
            "team": team,
            "attribution_pct": {k: (float(v) if v is not None else None) for k, v in attr_pct.items()},
            "hcp_counts": {k: (int(v) if v is not None else None) for k, v in hcp_counts.items()},
            "touchpoint_counts": {k: (int(v) if v is not None else None) for k, v in tp_counts.items()},
        })

    # ── Team Level Summary ──────────────────────────────────────────
    team_summary: Dict[str, Dict] = {}
    for r in rows:
        channel = r.get("Channel", "")
        team = channel.split("_")[0] if "_" in channel else channel
        pct = float(r.get("Attribution_Pct_All_HCPs") or 0.0)
        refs = int(r.get("no_of_prescribers_All_HCPs") or 0)
        if team not in team_summary:
            team_summary[team] = {"attribution_pct": 0.0, "referrals_attributed": 0}
        team_summary[team]["attribution_pct"] += pct
        team_summary[team]["referrals_attributed"] += refs

    return {
        "scenario_id": scenario_id,
        "run_params": {
            "product": first.get("run_product"),
            "start_date": str(first.get("run_start") or ""),
            "end_date": str(first.get("run_end") or ""),
            "attribution_level": first.get("run_level"),
            "hcp_segment": first.get("run_segment"),
        },
        "run_timestamp": str(first.get("run_timestamp") or ""),
        "summary_kpis": {
            "total_hcps_in_universe": total_hcps,
            "total_referrals": total_referrals,
            "total_touchpoints": total_touchpoints,
            "total_prescribers": total_prescribers,
        },
        "channel_attribution": channel_attribution,
        "team_level_summary": team_summary,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Job Trigger & Status
# ─────────────────────────────────────────────────────────────────────────────

SEGMENT_MAP = {
    "all_hcps": "1",
    "cluster": "2",
    "lob": "3",
    "competitor_drug": "4",
}

LEVEL_MAP = {
    "touchpoint": "touchpoint level",
    "channel": "channel level",
    "team": "team level",
}


def trigger_databricks_job(
    settings: Settings,
    scenario_id: str,
    product: str,
    start_date: str,
    end_date: str,
    attribution_level: str,
    hcp_segment: str,
) -> int:
    """Submit a Databricks job run and return the run_id."""
    client = _get_sdk_client(settings)
    run = client.jobs.run_now(
        job_id=settings.databricks_job_id,
        notebook_params={
            "scenario_id": scenario_id,
        },
        python_params=[
            "--start_date", start_date,
            "--end_date", end_date,
            "--product", product,
            "--level", LEVEL_MAP.get(attribution_level, "touchpoint level"),
            "--segment", SEGMENT_MAP.get(hcp_segment, "1"),
        ],
    )
    return run.run_id


def get_run_status(settings: Settings, databricks_run_id: int) -> Dict[str, Any]:
    """Poll the Databricks Jobs API and map state to our enum."""
    client = _get_sdk_client(settings)
    run = client.jobs.get_run(run_id=databricks_run_id)

    lifecycle = run.state.life_cycle_state
    result_state = run.state.result_state

    if lifecycle in (RunLifeCycleState.PENDING, RunLifeCycleState.QUEUED):
        status = "QUEUED"
        message = "Databricks job is queued."
        progress = 5
    elif lifecycle == RunLifeCycleState.RUNNING:
        status = "RUNNING"
        message = run.state.state_message or "Model is computing…"
        # Rough progress estimate from elapsed time (job usually takes ~90s)
        import time
        elapsed = int(time.time()) - int(run.start_time / 1000) if run.start_time else 0
        progress = min(int(elapsed / 90 * 90), 90)
    elif lifecycle == RunLifeCycleState.TERMINATED:
        if result_state == RunResultState.SUCCESS:
            status = "SUCCESS"
            message = "Databricks job completed successfully."
            progress = 100
        else:
            status = "FAILED"
            message = run.state.state_message or "Job failed on Databricks."
            progress = 0
    else:
        status = "RUNNING"
        message = str(lifecycle)
        progress = 50

    elapsed = 0
    if run.start_time:
        import time
        elapsed = int(time.time()) - int(run.start_time / 1000)

    return {
        "status": status,
        "progress_pct": progress,
        "message": message,
        "elapsed_seconds": elapsed,
    }
