# backend/routers/export.py
"""
Export router — generates CSV or PDF reports from scenario results.
"""
from __future__ import annotations

import io
import csv
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from config import Settings, get_settings
from routers.auth import get_current_user
from schemas.scenarios import ScenarioStatus
from services.scenario_store import scenario_store
import services.databricks_client as db

router = APIRouter(prefix="/export", tags=["export"])


def _make_csv(results: dict, scenario_name: str) -> bytes:
    """Build a CSV of channel attribution results."""
    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        "Scenario", "Channel", "Team",
        "Attribution % All HCPs",
        "Attribution % High Performer", "Attribution % Moderate Performer",
        "Attribution % Average Performer", "Attribution % Low Performer",
        "Attribution % Near Sleeping", "Attribution % Sleeping", "Attribution % Unresponsive",
        "HCPs All", "Touchpoints All",
    ])

    for ch in results.get("channel_attribution", []):
        pct = ch.get("attribution_pct", {})
        hcp = ch.get("hcp_counts", {})
        tp = ch.get("touchpoint_counts", {})
        writer.writerow([
            scenario_name,
            ch.get("channel"),
            ch.get("team"),
            pct.get("all_hcps"),
            pct.get("high_performer"),
            pct.get("moderate_performer"),
            pct.get("average_performer"),
            pct.get("low_performer"),
            pct.get("near_sleeping"),
            pct.get("sleeping"),
            pct.get("unresponsive"),
            hcp.get("all_hcps"),
            tp.get("all_hcps"),
        ])
    return output.getvalue().encode("utf-8")


def _make_pdf(results: dict, scenario_name: str, kpis: dict) -> bytes:
    """Build a simple PDF report using reportlab."""
    from reportlab.lib.pagesizes import letter
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    story.append(Paragraph(f"UTC Channel Attribution Report", styles["Title"]))
    story.append(Paragraph(f"Scenario: {scenario_name}", styles["Heading2"]))
    story.append(Paragraph(f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]))
    story.append(Spacer(1, 12))

    # KPIs
    kpi_data = [
        ["Metric", "Value"],
        ["Total HCPs", str(kpis.get("total_hcps_in_universe", "—"))],
        ["Total Referrals", str(kpis.get("total_referrals", "—"))],
        ["Total Touchpoints", str(kpis.get("total_touchpoints", "—"))],
        ["Total Prescribers", str(kpis.get("total_prescribers", "—"))],
    ]
    kpi_table = Table(kpi_data, colWidths=[200, 200])
    kpi_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1B2632")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ]))
    story.append(kpi_table)
    story.append(Spacer(1, 16))

    # Channel attribution table
    story.append(Paragraph("Channel Attribution (All HCPs)", styles["Heading3"]))
    ch_data = [["Channel", "Team", "Attribution %", "HCPs", "Touchpoints"]]
    for ch in results.get("channel_attribution", [])[:20]:
        pct = ch.get("attribution_pct", {})
        ch_data.append([
            ch.get("channel", ""),
            ch.get("team", ""),
            f"{(pct.get('all_hcps') or 0) * 100:.1f}%",
            str(ch.get("hcp_counts", {}).get("all_hcps") or ""),
            str(ch.get("touchpoint_counts", {}).get("all_hcps") or ""),
        ])
    ch_table = Table(ch_data, colWidths=[160, 60, 80, 80, 80])
    ch_table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#FFB162")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F5F3F0")]),
    ]))
    story.append(ch_table)

    doc.build(story)
    return buf.getvalue()


@router.get("/{scenario_id}")
def export_scenario(
    scenario_id: str,
    format: str = Query(default="csv", pattern="^(csv|pdf)$"),
    include_segments: bool = Query(default=True),
    settings: Settings = Depends(get_settings),
    _: dict = Depends(get_current_user),
):
    meta = scenario_store.get(scenario_id)
    if not meta:
        raise HTTPException(status_code=404, detail=f"Scenario '{scenario_id}' not found.")
    if meta.status != ScenarioStatus.SUCCESS:
        raise HTTPException(status_code=409, detail="Scenario results not ready.")

    results = db.get_scenario_results_from_delta(settings, scenario_id)
    if not results:
        raise HTTPException(status_code=404, detail="No results found in Delta.")

    stamp = datetime.utcnow().strftime("%Y%m%d")
    safe_name = meta.scenario_name.replace(" ", "_")[:40]

    if format == "csv":
        content = _make_csv(results, meta.scenario_name)
        return StreamingResponse(
            io.BytesIO(content),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={safe_name}_{stamp}.csv"},
        )
    else:  # pdf
        content = _make_pdf(results, meta.scenario_name, results.get("summary_kpis", {}))
        return StreamingResponse(
            io.BytesIO(content),
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={safe_name}_{stamp}.pdf"},
        )
