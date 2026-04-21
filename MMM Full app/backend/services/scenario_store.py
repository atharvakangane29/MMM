# backend/services/scenario_store.py
"""
In-memory scenario metadata store.
Tracks scenario status, Databricks run IDs, and cached results.

In production you would persist this to a database (e.g. SQLite / Postgres).
The interface is kept intentionally thin so it can be swapped out.
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Dict, List, Optional

from schemas.scenarios import ScenarioMeta, ScenarioStatus


class ScenarioStore:
    """Thread-safe enough for a single-worker FastAPI process."""

    def __init__(self) -> None:
        self._store: Dict[str, ScenarioMeta] = {}

    # ── CRUD ───────────────────────────────────────────────────────────────

    def create(
        self,
        scenario_name: str,
        product: str,
        start_date: str,
        end_date: str,
        attribution_level: str,
        hcp_segment: str,
        notes: Optional[str] = None,
    ) -> ScenarioMeta:
        scenario_id = str(uuid.uuid4())
        meta = ScenarioMeta(
            scenario_id=scenario_id,
            scenario_name=scenario_name,
            product=product,
            start_date=start_date,
            end_date=end_date,
            attribution_level=attribution_level,
            hcp_segment=hcp_segment,
            notes=notes,
            status=ScenarioStatus.QUEUED,
            created_at=datetime.now(timezone.utc).isoformat(),
        )
        self._store[scenario_id] = meta
        return meta

    def get(self, scenario_id: str) -> Optional[ScenarioMeta]:
        return self._store.get(scenario_id)

    def list_all(
        self,
        product: Optional[str] = None,
        status: Optional[ScenarioStatus] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> Dict:
        items = list(self._store.values())

        # Filter
        if product:
            items = [s for s in items if s.product.upper() == product.upper()]
        if status:
            items = [s for s in items if s.status == status]

        # Sort newest first
        items.sort(key=lambda s: s.created_at or "", reverse=True)

        total = len(items)
        start = (page - 1) * page_size
        end = start + page_size
        return {
            "total": total,
            "page": page,
            "page_size": page_size,
            "scenarios": [s.model_dump() for s in items[start:end]],
        }

    def update_status(
        self,
        scenario_id: str,
        status: ScenarioStatus,
        databricks_run_id: Optional[int] = None,
        error_message: Optional[str] = None,
    ) -> Optional[ScenarioMeta]:
        meta = self._store.get(scenario_id)
        if not meta:
            return None
        meta.status = status
        if databricks_run_id is not None:
            meta.databricks_run_id = databricks_run_id
        if error_message is not None:
            meta.error_message = error_message
        if status == ScenarioStatus.SUCCESS:
            meta.completed_at = datetime.now(timezone.utc).isoformat()
        return meta

    def soft_delete(self, scenario_id: str) -> bool:
        if scenario_id in self._store:
            del self._store[scenario_id]
            return True
        return False


# Singleton — shared across all requests in the process lifetime
scenario_store = ScenarioStore()
