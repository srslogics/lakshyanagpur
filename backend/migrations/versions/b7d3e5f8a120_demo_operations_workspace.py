"""add isolated Operations demo account

Revision ID: b7d3e5f8a120
Revises: a4e7c2d91b30
"""

from __future__ import annotations

from datetime import datetime, timezone
from hashlib import pbkdf2_hmac

from alembic import op
import sqlalchemy as sa


revision = "b7d3e5f8a120"
down_revision = "a4e7c2d91b30"
branch_labels = None
depends_on = None

DEMO_USER_ID = "usr_operations_demo"
DEMO_USERNAME = "demo-erp"
DEMO_PASSWORD = "demo123"
DEMO_SALT = "7f696a4b5c6d7e8f90123456789abcde"


def _password_hash() -> str:
    digest = pbkdf2_hmac(
        "sha256",
        DEMO_PASSWORD.encode(),
        bytes.fromhex(DEMO_SALT),
        210_000,
    ).hex()
    return f"pbkdf2_sha256${DEMO_SALT}${digest}"


def upgrade():
    op.add_column("users", sa.Column("username", sa.String(length=32), nullable=True))
    op.create_index("ix_users_username", "users", ["username"], unique=True)

    users = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("username", sa.String),
        sa.column("mobile", sa.String),
        sa.column("email", sa.String),
        sa.column("full_name", sa.String),
        sa.column("password_hash", sa.String),
        sa.column("role", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("must_change_password", sa.Boolean),
        sa.column("token_version", sa.Integer),
        sa.column("is_test_account", sa.Boolean),
        sa.column("created_at", sa.DateTime(timezone=True)),
        sa.column("updated_at", sa.DateTime(timezone=True)),
    )
    bind = op.get_bind()
    now = datetime.now(timezone.utc)
    existing_id = bind.execute(
        sa.select(users.c.id).where(
            sa.or_(users.c.id == DEMO_USER_ID, users.c.username == DEMO_USERNAME)
        )
    ).scalar_one_or_none()
    values = {
        "username": DEMO_USERNAME,
        "mobile": None,
        "email": None,
        "full_name": "ERP Demo",
        "password_hash": _password_hash(),
        "role": "demo",
        "is_active": True,
        "must_change_password": False,
        "token_version": 0,
        "is_test_account": False,
        "updated_at": now,
    }
    if existing_id:
        bind.execute(sa.update(users).where(users.c.id == existing_id).values(**values))
    else:
        bind.execute(
            sa.insert(users).values(
                id=DEMO_USER_ID,
                created_at=now,
                **values,
            )
        )


def downgrade():
    users = sa.table(
        "users",
        sa.column("id", sa.String),
        sa.column("username", sa.String),
    )
    op.get_bind().execute(
        sa.delete(users).where(
            sa.or_(users.c.id == DEMO_USER_ID, users.c.username == DEMO_USERNAME)
        )
    )
    op.drop_index("ix_users_username", table_name="users")
    op.drop_column("users", "username")
