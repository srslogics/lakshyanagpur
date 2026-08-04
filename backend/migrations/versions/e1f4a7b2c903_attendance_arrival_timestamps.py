"""attendance arrival timestamps

Revision ID: e1f4a7b2c903
Revises: 0d8a3f2026c1
"""

from alembic import op
import sqlalchemy as sa


revision = "e1f4a7b2c903"
down_revision = "0d8a3f2026c1"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("attendance_entries") as batch:
        batch.add_column(sa.Column("arrival_at", sa.DateTime(timezone=True), nullable=True))


def downgrade():
    with op.batch_alter_table("attendance_entries") as batch:
        batch.drop_column("arrival_at")
