# backend/config.py — centralised settings loaded from .env
from __future__ import annotations
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """All configuration comes from environment variables (or .env file).
    No hardcoded secrets, no hardcoded URLs.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Databricks ──────────────────────────────────────────────
    databricks_host: str
    databricks_token: str
    databricks_http_path: str
    databricks_job_id: int

    # ── Unity Catalog defaults ───────────────────────────────────
    default_catalog: str = "coe-consultant-catalog"
    default_schema: str = "results"
    master_table: str = "channel_attribution_master_test"
    journey_schema: str = "channel_attribution"

    # ── Auth ────────────────────────────────────────────────────
    api_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 8

    # ── App users (stored server-side, comma-separated email:pw:role) ──
    app_users: str  # e.g. "analyst@utc.com:pass:analyst,admin@utc.com:pass:admin"

    # ── CORS ────────────────────────────────────────────────────
    cors_origins: str = "http://localhost:3000,http://localhost:5500,http://127.0.0.1:5500"

    # ── Export ──────────────────────────────────────────────────
    max_export_scenarios: int = 10

    # ── Computed helpers ────────────────────────────────────────
    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def full_master_table(self) -> str:
        """Fully-qualified Delta table name."""
        return f"`{self.default_catalog}`.{self.default_schema}.{self.master_table}"

    @property
    def user_credentials(self) -> List[dict]:
        """Parse APP_USERS env var into a list of dicts."""
        users = []
        for entry in self.app_users.split(","):
            parts = entry.strip().split(":")
            if len(parts) == 3:
                users.append({"email": parts[0], "password": parts[1], "role": parts[2]})
        return users


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
