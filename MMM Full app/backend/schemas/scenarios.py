# backend/schemas/scenarios.py
from __future__ import annotations
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class ScenarioStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"


class AttributionLevel(str, Enum):
    touchpoint = "touchpoint"
    channel = "channel"
    team = "team"


class HCPSegment(str, Enum):
    cluster = "cluster"
    lob = "lob"
    competitor_drug = "competitor_drug"
    all_hcps = "all_hcps"


class Product(str, Enum):
    TYVASO = "TYVASO"
    REMODULIN = "REMODULIN"
    ORENITRAM = "ORENITRAM"
    TREPROSTINIL = "TREPROSTINIL"
    ALL = "ALL"


# ── Request / Response schemas ────────────────────────────────────────────────

class RunScenarioRequest(BaseModel):
    scenario_name: str
    product: Product
    start_date: str   # YYYY-MM-DD
    end_date: str     # YYYY-MM-DD
    attribution_level: AttributionLevel
    hcp_segment: HCPSegment
    notes: Optional[str] = None


class ScenarioMeta(BaseModel):
    scenario_id: str
    scenario_name: str
    product: str
    start_date: str
    end_date: str
    attribution_level: str
    hcp_segment: str
    status: ScenarioStatus = ScenarioStatus.QUEUED
    databricks_run_id: Optional[int] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    notes: Optional[str] = None
    error_message: Optional[str] = None


class RunScenarioResponse(BaseModel):
    scenario_id: str
    scenario_name: str
    status: ScenarioStatus
    created_at: str
    estimated_runtime_seconds: int = 90
    message: str


class StatusResponse(BaseModel):
    scenario_id: str
    status: ScenarioStatus
    progress_pct: int
    message: str
    elapsed_seconds: int


class CompareRequest(BaseModel):
    scenario_ids: list[str]
    comparison_dimension: Optional[str] = None
    hcp_segment_filter: Optional[str] = "all_hcps"


class ValidateTableRequest(BaseModel):
    catalog: str
    schema: str
    table: str
