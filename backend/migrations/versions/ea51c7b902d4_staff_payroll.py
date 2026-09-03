"""Add auditable monthly staff payroll calculations."""

from alembic import op
import sqlalchemy as sa

revision = "ea51c7b902d4"
down_revision = "c2a9f4e71d60"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "staff_payroll",
        sa.Column("id", sa.String(64), primary_key=True),
        sa.Column("person_key", sa.String(150), nullable=False),
        sa.Column("month", sa.String(7), nullable=False),
        sa.Column("monthly_salary", sa.Numeric(14, 2), nullable=False),
        sa.Column("advance_given", sa.Numeric(14, 2), nullable=False),
        sa.Column("absent_days", sa.Integer(), nullable=False),
        sa.Column("attendance_fingerprint", sa.String(64), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False),
        sa.Column("snapshot", sa.JSON(), nullable=False),
        sa.Column("updated_by", sa.String(64), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.UniqueConstraint("person_key", "month", name="uq_staff_payroll_month"),
    )
    op.create_index("ix_staff_payroll_person_key", "staff_payroll", ["person_key"])
    op.create_index("ix_staff_payroll_month", "staff_payroll", ["month"])


def downgrade():
    op.drop_table("staff_payroll")
