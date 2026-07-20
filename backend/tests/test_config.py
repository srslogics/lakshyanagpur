from app.config import normalize_database_url


def test_postgres_provider_urls_use_psycopg3_dialect():
    assert normalize_database_url("postgresql://user:pass@db.example/postgres") == (
        "postgresql+psycopg://user:pass@db.example/postgres"
    )
    assert normalize_database_url("postgres://user:pass@db.example/postgres") == (
        "postgresql+psycopg://user:pass@db.example/postgres"
    )


def test_explicit_dialects_and_sqlite_urls_are_preserved():
    assert normalize_database_url("postgresql+psycopg://user:pass@db.example/postgres") == (
        "postgresql+psycopg://user:pass@db.example/postgres"
    )
    assert normalize_database_url("sqlite:///./lakshya_erp.db") == "sqlite:///./lakshya_erp.db"
