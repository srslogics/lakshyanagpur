from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BASE_DIR / ".env")


def normalize_database_url(value: str) -> str:
    """Select Psycopg 3 explicitly for provider-style PostgreSQL URLs."""
    url = value.strip()
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url.removeprefix("postgres://")
    if url.startswith("postgresql://"):
        return "postgresql+psycopg://" + url.removeprefix("postgresql://")
    return url


class Settings:
    environment: str = os.getenv("APP_ENV", "development").strip().lower()
    is_render: bool = bool(os.getenv("RENDER"))
    database_url: str = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./lakshya_erp.db"))
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    cors_origins: list[str] = [item.strip() for item in os.getenv("CORS_ORIGINS", "").split(",") if item.strip()]
    secret_key: str = os.getenv("SECRET_KEY", "development-only-change-me")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
    seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "false").lower() == "true"
    allow_legacy_email_login: bool = os.getenv("ALLOW_LEGACY_EMAIL_LOGIN", "false").lower() == "true"
    database_pool_pre_ping: bool = os.getenv("DATABASE_POOL_PRE_PING", "false").lower() == "true"


settings = Settings()


def validate_runtime_settings(runtime: Settings = settings) -> None:
    """Fail fast when a hosted process would otherwise use development defaults."""
    if not (runtime.is_render or runtime.environment in {"production", "prod"}):
        return
    errors: list[str] = []
    if runtime.database_url.startswith("sqlite"):
        errors.append("DATABASE_URL must point to PostgreSQL")
    if runtime.secret_key == "development-only-change-me" or len(runtime.secret_key) < 32:
        errors.append("SECRET_KEY must be a random value of at least 32 characters")
    if runtime.seed_demo_data:
        errors.append("SEED_DEMO_DATA must be false")
    if errors:
        raise RuntimeError("Invalid production configuration: " + "; ".join(errors))


validate_runtime_settings()
