"""Transaction-scoped serialization for read/check/write workflows."""
from hashlib import sha256

from sqlalchemy import text


def transaction_lock(db, resource):
    # Production uses PostgreSQL. SQLite tests do not simulate concurrent
    # transactions and must not be used to certify this guarantee.
    if db.get_bind().dialect.name == "postgresql":
        key = int.from_bytes(sha256(resource.encode()).digest()[:8], "big", signed=True)
        db.execute(text("SELECT pg_advisory_xact_lock(:key)"), {"key": key})
