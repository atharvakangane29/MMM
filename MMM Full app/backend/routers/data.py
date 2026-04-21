# backend/routers/data.py
"""
Data quality report and table preview endpoints.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from config import Settings, get_settings
from routers.auth import get_current_user
import services.databricks_client as db

router = APIRouter(prefix="/data", tags=["data"])


@router.get("/report")
def data_report(
    catalog: str = Query(...),
    schema: str = Query(...),
    table: str = Query(...),
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    try:
        return db.get_data_report(settings, catalog, schema, table)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/preview")
def table_preview(
    catalog: str = Query(...),
    schema: str = Query(...),
    table: str = Query(...),
    limit: int = Query(default=5, le=100),
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    try:
        rows = db.get_table_preview(settings, catalog, schema, table, limit)
        return {"rows": rows, "count": len(rows)}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
