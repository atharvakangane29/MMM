# backend/routers/databricks.py
"""
Databricks metadata endpoints: catalog/schema/table discovery + schema validation.
"""
from __future__ import annotations
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

from config import Settings, get_settings
from routers.auth import get_current_user
from schemas.scenarios import ValidateTableRequest
import services.databricks_client as db

router = APIRouter(prefix="/databricks", tags=["databricks"])


def _settings_dep() -> Settings:
    return get_settings()


@router.get("/catalogs")
def list_catalogs(
    settings: Annotated[Settings, Depends(_settings_dep)],
    _: Annotated[dict, Depends(get_current_user)],
):
    try:
        catalogs = db.list_catalogs(settings)
        return {"catalogs": catalogs}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/schemas")
def list_schemas(
    catalog: str = Query(..., description="Unity Catalog catalog name"),
    settings: Settings = Depends(_settings_dep),
    _: dict = Depends(get_current_user),
):
    try:
        schemas = db.list_schemas(settings, catalog)
        return {"catalog": catalog, "schemas": schemas}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.get("/tables")
def list_tables(
    catalog: str = Query(...),
    schema: str = Query(...),
    settings: Settings = Depends(_settings_dep),
    _: dict = Depends(get_current_user),
):
    try:
        tables = db.list_tables(settings, catalog, schema)
        return {"tables": tables}
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc


@router.post("/validate-table")
def validate_table(
    body: ValidateTableRequest,
    settings: Settings = Depends(_settings_dep),
    _: dict = Depends(get_current_user),
):
    try:
        result = db.validate_table(settings, body.catalog, body.schema, body.table)
        return result
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
