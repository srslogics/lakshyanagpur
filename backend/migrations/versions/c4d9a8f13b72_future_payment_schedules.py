"""add future payment schedules"""

from alembic import op
import sqlalchemy as sa


revision = "c4d9a8f13b72"
down_revision = "8ae21f43d760"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fee_installments",
        sa.Column("id", sa.String(length=64), nullable=False),
        sa.Column("student_id", sa.String(length=64), nullable=False),
        sa.Column("fee_agreement_id", sa.String(length=64), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column("expected_method", sa.String(length=24), nullable=False),
        sa.Column("notes", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=24), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["fee_agreement_id"], ["fee_agreements.id"]),
        sa.ForeignKeyConstraint(["student_id"], ["students.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_fee_installments_created_by",
        "fee_installments",
        ["created_by"],
    )
    op.create_index(
        "ix_fee_installments_due_date",
        "fee_installments",
        ["due_date"],
    )
    op.create_index(
        "ix_fee_installments_fee_agreement_id",
        "fee_installments",
        ["fee_agreement_id"],
    )
    op.create_index(
        "ix_fee_installments_status",
        "fee_installments",
        ["status"],
    )
    op.create_index(
        "ix_fee_installments_student_id",
        "fee_installments",
        ["student_id"],
    )


def downgrade():
    op.drop_index(
        "ix_fee_installments_student_id",
        table_name="fee_installments",
    )
    op.drop_index(
        "ix_fee_installments_status",
        table_name="fee_installments",
    )
    op.drop_index(
        "ix_fee_installments_fee_agreement_id",
        table_name="fee_installments",
    )
    op.drop_index(
        "ix_fee_installments_due_date",
        table_name="fee_installments",
    )
    op.drop_index(
        "ix_fee_installments_created_by",
        table_name="fee_installments",
    )
    op.drop_table("fee_installments")
