# backend/main.py
"""
UTC Channel Attribution MMM Platform — FastAPI Backend
======================================================
Start with:   uvicorn main:app --reload --port 8000
Production:   uvicorn main:app --host 0.0.0.0 --port 8000 --workers 2
"""
from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from routers import auth, compare, data, databricks, export, health, scenarios

# ─────────────────────────────────────────────────────────────────────────────
# Logging
# ─────────────────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s — %(message)s")
logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────────────────────
# Lifespan
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    logger.info("═══ UTC Channel Attribution Platform starting ═══")
    logger.info(f"  Databricks host : {settings.databricks_host}")
    logger.info(f"  Master table    : {settings.full_master_table}")
    logger.info(f"  CORS origins    : {settings.cors_origins_list}")
    yield
    logger.info("═══ Platform shutting down ═══")


# ─────────────────────────────────────────────────────────────────────────────
# App
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="UTC Channel Attribution MMM Platform",
    version="1.0.0",
    description=(
        "FastAPI backend for the 9-step Multi-Channel Attribution & "
        "Mixed Marketing Model platform. Connects to Databricks Unity Catalog."
    ),
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# ─────────────────────────────────────────────────────────────────────────────
# CORS — origins come from env, never hardcoded
# ─────────────────────────────────────────────────────────────────────────────
settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────────────────────────────────────
# Global error handler
# ─────────────────────────────────────────────────────────────────────────────
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    from datetime import datetime, timezone
    logger.exception(f"Unhandled error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": str(exc),
                "details": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        },
    )

# ─────────────────────────────────────────────────────────────────────────────
# Routers — all mounted under /api/v1
# ─────────────────────────────────────────────────────────────────────────────
PREFIX = "/api/v1"

app.include_router(auth.router, prefix=PREFIX)
app.include_router(databricks.router, prefix=PREFIX)
app.include_router(data.router, prefix=PREFIX)
app.include_router(scenarios.router, prefix=PREFIX)
app.include_router(compare.router, prefix=PREFIX)
app.include_router(export.router, prefix=PREFIX)
app.include_router(health.router, prefix=PREFIX)

# ─────────────────────────────────────────────────────────────────────────────
# Root redirect
# ─────────────────────────────────────────────────────────────────────────────
@app.get("/", include_in_schema=False)
def root():
    return {"message": "UTC Channel Attribution Platform API", "docs": "/api/docs"}
