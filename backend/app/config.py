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
    database_url: str = normalize_database_url(os.getenv("DATABASE_URL", "sqlite:///./lakshya_erp.db"))
    app_host: str = os.getenv("APP_HOST", "127.0.0.1")
    app_port: int = int(os.getenv("APP_PORT", "8000"))
    cors_origins: list[str] = [item.strip() for item in os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",") if item.strip()]
    secret_key: str = os.getenv("SECRET_KEY", "development-only-change-me")
    access_token_minutes: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "480"))
    seed_demo_data: bool = os.getenv("SEED_DEMO_DATA", "false").lower() == "true"


settings = Settings()
