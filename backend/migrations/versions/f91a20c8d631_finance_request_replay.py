"""Persist idempotent financial command responses."""
from alembic import op
import sqlalchemy as sa

revision = "f91a20c8d631"
down_revision = "e73b91c8f240"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "finance_requests",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("fingerprint", sa.String(64), nullable=False),
        sa.Column("response", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade():
    op.drop_table("finance_requests")
