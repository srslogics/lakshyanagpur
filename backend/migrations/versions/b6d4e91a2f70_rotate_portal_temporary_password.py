"""rotate portal temporary password

Revision ID: b6d4e91a2f70
Revises: a4c9d2e7f610
"""

from hashlib import pbkdf2_hmac
from secrets import token_hex

from alembic import op
import sqlalchemy as sa


revision = "b6d4e91a2f70"
down_revision = "a4c9d2e7f610"
branch_labels = None
depends_on = None


TEMPORARY_PASSWORD = "Lakshaya@2026"
PORTAL_ROLES = (
    "student",
    "parent",
    "parent_student",
    "faculty",
    "attendance_operator",
)


def _hash_password(password: str) -> str:
    salt = token_hex(16)
    digest = pbkdf2_hmac(
        "sha256",
        password.encode(),
        bytes.fromhex(salt),
        210_000,
    ).hex()
    return f"pbkdf2_sha256${salt}${digest}"


def upgrade():
    # Rotate every active portal account requested by the institute. Operations
    # and owner accounts are intentionally excluded from the shared password.
    bind = op.get_bind()
    account_ids = bind.execute(
        sa.text(
            """
            SELECT id
              FROM users
             WHERE is_active = true
               AND is_test_account = false
               AND role IN (
                   'student',
                   'parent',
                   'parent_student',
                   'faculty',
                   'attendance_operator'
               )
            """
        )
    ).scalars()

    update_account = sa.text(
        """
        UPDATE users
           SET password_hash = :password_hash,
               must_change_password = true,
               token_version = token_version + 1
         WHERE id = :account_id
        """
    )
    for account_id in account_ids:
        bind.execute(
            update_account,
            {
                "account_id": account_id,
                "password_hash": _hash_password(TEMPORARY_PASSWORD),
            },
        )


def downgrade():
    # Previous password hashes cannot be reconstructed safely.
    pass
