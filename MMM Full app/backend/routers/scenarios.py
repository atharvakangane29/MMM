# backend/routers/scenarios.py
"""
Scenario lifecycle: create, list, status poll, results, delete.
"""
from __future__ import annotations

import logging
from typing import Annotated, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status

from config import Settings, get_settings
from routers.auth import get_current_user
from schemas.scenarios import (
    RunScenarioRequest,
    RunScenarioResponse,
    ScenarioStatus,
    StatusResponse,
)
from services.scenario_store import scenario_store
import services.databricks_client as db

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/scenarios", tags=["scenarios"])


# ─────────────────────────────────────────────────────────────────────────────
# Background job trigger
# ─────────────────────────────────────────────────────────────────────────────

def _trigger_job_background(scenario_id: str, req: RunScenarioRequest, settings: Settings):
    """Fired by FastAPI BackgroundTasks after 202 is returned."""
    try:
        run_id = db.trigger_databricks_job(
            settings,
            scenario_id=scenario_id,
            product=req.product.value,
            start_date=req.start_date,
            end_date=req.end_date,
            attribution_level=req.attribution_level.value,
            hcp_segment=req.hcp_segment.value,
        )
        scenario_store.update_status(scenario_id, ScenarioStatus.RUNNING, databricks_run_id=run_id)
        logger.info(f"[scenario {scenario_id}] Databricks run_id={run_id} started.")
    except Exception as exc:
        logger.error(f"[scenario {scenario_id}] Job trigger failed: {exc}")
        scenario_store.update_status(scenario_id, ScenarioStatus.FAILED, error_message=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Routes
# ─────────────────────────────────────────────────────────────────────────────

@router.post("/run", status_code=status.HTTP_202_ACCEPTED, response_model=RunScenarioResponse)
def run_scenario(
    req: RunScenarioRequest,
    background_tasks: BackgroundTasks,
    settings: Annotated[Settings, Depends(get_settings)],
    _: Annotated[dict, Depends(get_current_user)],
):
    meta = scenario_store.create(
        scenario_name=req.scenario_name,
        product=req.product.value,
        start_date=req.start_date,
        end_date=req.end_date,
        attribution_level=req.attribution_level.value,
        hcp_segment=req.hcp_segment.value,
        notes=req.notes,
    )
    background_tasks.add_task(_trigger_job_background, meta.scenario_id, req, settings)

    return RunScenarioResponse(
        scenario_id=meta.scenario_id,
        scenario_name=meta.scenario_name,
        status=ScenarioStatus.QUEUED,
        created_at=meta.created_at or "",
        message="Databricks job queued. Poll /scenarios/{id}/status for updates.",
    )


@router.get("")
def list_scenarios(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, le=100),
    product: Optional[str] = Query(default=None),
    status_filter: Optional[ScenarioStatus] = Query(default=None, alias="status"),
    _: dict = Depends(get_current_user),
):
    return scenario_store.list_all(product=product, status=status_filter, page=page, page_size=page_size)


@router.get("/{scenario_id}")
def get_scenario(scenario_id: str, _: dict = Depends(get_current_user)):
    meta = scenario_store.get(scenario_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return meta.model_dump()


@router.get("/{scenario_id}/status", response_model=StatusResponse)
def get_status(
    scenario_id: str,
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    meta = scenario_store.get(scenario_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")

    # If we have a Databricks run_id, poll the live status
    if meta.databricks_run_id and meta.status not in (ScenarioStatus.SUCCESS, ScenarioStatus.FAILED):
        try:
            live = db.get_run_status(settings, meta.databricks_run_id)
            new_status = ScenarioStatus(live["status"])
            if new_status != meta.status:
                scenario_store.update_status(scenario_id, new_status)
                meta.status = new_status
            return StatusResponse(
                scenario_id=scenario_id,
                status=new_status,
                progress_pct=live["progress_pct"],
                message=live["message"],
                elapsed_seconds=live["elapsed_seconds"],
            )
        except Exception as exc:
            logger.warning(f"[scenario {scenario_id}] Status poll failed: {exc}")

    # Return cached status
    progress_map = {
        ScenarioStatus.QUEUED: 0,
        ScenarioStatus.RUNNING: 50,
        ScenarioStatus.SUCCESS: 100,
        ScenarioStatus.FAILED: 0,
    }
    return StatusResponse(
        scenario_id=scenario_id,
        status=meta.status,
        progress_pct=progress_map.get(meta.status, 0),
        message=meta.error_message or f"Status: {meta.status.value}",
        elapsed_seconds=0,
    )


@router.get("/{scenario_id}/results")
def get_results(
    scenario_id: str,
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    meta = scenario_store.get(scenario_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    if meta.status != ScenarioStatus.SUCCESS:
        raise HTTPException(
            status_code=409,
            detail=f"Scenario is {meta.status.value} — poll /status first.",
        )

    results = db.get_scenario_results_from_delta(settings, scenario_id)
    if not results:
        raise HTTPException(status_code=404, detail="No results found in Delta table for this scenario.")

    return {"scenario_name": meta.scenario_name, **results}


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: str, _: dict = Depends(get_current_user)):
    if not scenario_store.soft_delete(scenario_id):
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    return {"scenario_id": scenario_id, "deleted": True, "message": "Scenario soft-deleted."}
