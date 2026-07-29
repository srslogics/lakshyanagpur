from types import SimpleNamespace

from app.config import validate_runtime_settings


def test_same_origin_production_does_not_require_cors_origins():
    runtime = SimpleNamespace(
        is_render=True,
        environment="production",
        database_url="postgresql+psycopg://example.invalid/database",
        secret_key="a-secure-production-secret-that-is-long-enough",
        cors_origins=[],
        seed_demo_data=False,
    )

    validate_runtime_settings(runtime)
