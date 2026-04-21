# backend/routers/compare.py
"""
Multi-scenario comparison engine.
"""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from config import Settings, get_settings
from routers.auth import get_current_user
from schemas.scenarios import CompareRequest, ScenarioStatus
from services.scenario_store import scenario_store
import services.databricks_client as db

router = APIRouter(prefix="/compare", tags=["compare"])


@router.post("")
def compare_scenarios(
    body: CompareRequest,
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    if len(body.scenario_ids) < 2:
        raise HTTPException(status_code=400, detail="At least 2 scenario IDs required.")
    if len(body.scenario_ids) > 4:
        raise HTTPException(status_code=400, detail="Maximum 4 scenarios can be compared.")

    seg_filter = body.hcp_segment_filter or "all_hcps"
    results_list = []

    for sid in body.scenario_ids:
        meta = scenario_store.get(sid)
        if not meta:
            raise HTTPException(status_code=404, detail=f"Scenario '{sid}' not found.")
        if meta.status != ScenarioStatus.SUCCESS:
            raise HTTPException(status_code=409, detail=f"Scenario '{sid}' is not yet complete.")

        results = db.get_scenario_results_from_delta(settings, sid)
        if not results:
            raise HTTPException(status_code=404, detail=f"No Delta results for scenario '{sid}'.")

        # Build channel list for this scenario
        channels = []
        for ch in results.get("channel_attribution", []):
            pct_value = (
                ch["attribution_pct"].get(seg_filter.lower())
                or ch["attribution_pct"].get("all_hcps")
                or 0.0
            )
            channels.append({"channel": ch["channel"], "attribution_pct": pct_value})

        results_list.append({
            "scenario_id": sid,
            "scenario_name": meta.scenario_name,
            "product": meta.product,
            "attribution_level": meta.attribution_level,
            "channels": channels,
        })

    # Build delta table (first two scenarios)
    delta = []
    if len(results_list) >= 2:
        ch_map_1 = {c["channel"]: c["attribution_pct"] for c in results_list[0]["channels"]}
        ch_map_2 = {c["channel"]: c["attribution_pct"] for c in results_list[1]["channels"]}
        all_channels = set(ch_map_1) | set(ch_map_2)
        for ch in sorted(all_channels):
            p1 = ch_map_1.get(ch, 0.0) or 0.0
            p2 = ch_map_2.get(ch, 0.0) or 0.0
            rel = round(((p1 - p2) / p2 * 100), 1) if p2 else None
            delta.append({
                "channel": ch,
                "scenario_1_pct": p1,
                "scenario_2_pct": p2,
                "absolute_diff": round(p1 - p2, 4),
                "relative_diff_pct": rel,
            })

    return {
        "comparison_id": f"cmp-{'-'.join(body.scenario_ids[:2])[:20]}",
        "scenarios": results_list,
        "delta": delta,
    }
