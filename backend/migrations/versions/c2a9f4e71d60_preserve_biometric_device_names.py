"""preserve biometric device names

Revision ID: c2a9f4e71d60
Revises: b7d3e5f8a120
"""

from alembic import op
import sqlalchemy as sa


revision = "c2a9f4e71d60"
down_revision = "b7d3e5f8a120"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "device_attendance_identities",
        sa.Column("device_name", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("device_attendance_identities", "device_name")
