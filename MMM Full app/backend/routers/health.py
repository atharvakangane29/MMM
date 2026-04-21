# backend/routers/health.py
from __future__ import annotations
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from config import Settings, get_settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health_check(settings: Settings = Depends(get_settings)):
    """
    Basic health check. Optionally pings Databricks.
    Returns quickly — suitable for load-balancer probes.
    """
    db_status = "unchecked"
    try:
        from databricks.sdk import WorkspaceClient
        ws = WorkspaceClient(host=settings.databricks_host, token=settings.databricks_token)
        ws.clusters.list()  # lightweight list call to verify connectivity
        db_status = "ok"
    except Exception:
        db_status = "unreachable"

    return {
        "status": "ok",
        "databricks_connection": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
