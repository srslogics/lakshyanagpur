from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings


class Base(DeclarativeBase):
    pass


connect_args = {}
if settings.database_url.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine_options = {
    "future": True,
    "echo": False,
    "connect_args": connect_args,
    "pool_pre_ping": settings.database_pool_pre_ping,
}
if not settings.database_url.startswith("sqlite"):
    engine_options.update({
        "pool_recycle": 1800,
        "pool_use_lifo": True,
        "pool_size": 5,
        "max_overflow": 5,
    })

engine = create_engine(settings.database_url, **engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
