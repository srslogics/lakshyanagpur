"""posted payment ledger and manual academic records

Revision ID: aa42d7e91c30
Revises: e5a21c7d9b40
Create Date: 2026-07-29
"""

from alembic import op
import sqlalchemy as sa


revision = "aa42d7e91c30"
down_revision = "e5a21c7d9b40"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("student_academic_profiles") as batch:
        batch.alter_column("import_batch_id", existing_type=sa.String(length=64), nullable=True)
    with op.batch_alter_table("student_subject_selections") as batch:
        batch.alter_column("import_batch_id", existing_type=sa.String(length=64), nullable=True)
    with op.batch_alter_table("fee_agreements") as batch:
        batch.alter_column("legacy_import_id", existing_type=sa.String(length=80), nullable=True)
    with op.batch_alter_table("payment_transactions") as batch:
        batch.alter_column("legacy_import_id", existing_type=sa.String(length=80), nullable=True)
        batch.alter_column("legacy_line_number", existing_type=sa.Integer(), nullable=True)
        batch.add_column(sa.Column("receipt_number", sa.String(length=48), nullable=True))
        batch.add_column(sa.Column("reference", sa.String(length=255), nullable=True))
        batch.add_column(sa.Column("notes", sa.Text(), nullable=False, server_default=""))
        batch.add_column(sa.Column("related_transaction_id", sa.String(length=64), nullable=True))
        batch.add_column(sa.Column("created_by", sa.String(length=64), nullable=True))
        batch.create_index(
            "ix_payment_transactions_receipt_number",
            ["receipt_number"],
            unique=True,
        )
        batch.create_index("ix_payment_transactions_related_transaction_id", ["related_transaction_id"])
        batch.create_index("ix_payment_transactions_created_by", ["created_by"])
        batch.create_foreign_key(
            "fk_payment_transactions_related_transaction_id",
            "payment_transactions",
            ["related_transaction_id"],
            ["id"],
        )
        batch.create_foreign_key(
            "fk_payment_transactions_created_by",
            "users",
            ["created_by"],
            ["id"],
        )

    op.execute(
        "UPDATE enrollments SET program = 'Boards' "
        "WHERE lower(program) IN ('boards 11th & 12th tuition', 'board')"
    )
    op.execute(
        "UPDATE batches SET program = 'Boards' "
        "WHERE lower(program) IN ('boards 11th & 12th tuition', 'board')"
    )
    op.execute(
        "UPDATE subjects SET program = 'Boards' "
        "WHERE lower(program) IN ('boards 11th & 12th tuition', 'board')"
    )
    op.execute(
        "UPDATE student_academic_profiles SET source_stream = 'Boards' "
        "WHERE lower(source_stream) IN ('boards 11th & 12th tuition', 'board')"
    )


def downgrade():
    with op.batch_alter_table("payment_transactions") as batch:
        batch.drop_constraint("fk_payment_transactions_created_by", type_="foreignkey")
        batch.drop_constraint("fk_payment_transactions_related_transaction_id", type_="foreignkey")
        batch.drop_index("ix_payment_transactions_created_by")
        batch.drop_index("ix_payment_transactions_related_transaction_id")
        batch.drop_index("ix_payment_transactions_receipt_number")
        batch.drop_column("created_by")
        batch.drop_column("related_transaction_id")
        batch.drop_column("notes")
        batch.drop_column("reference")
        batch.drop_column("receipt_number")
        batch.alter_column("legacy_line_number", existing_type=sa.Integer(), nullable=False)
        batch.alter_column("legacy_import_id", existing_type=sa.String(length=80), nullable=False)
    with op.batch_alter_table("fee_agreements") as batch:
        batch.alter_column("legacy_import_id", existing_type=sa.String(length=80), nullable=False)
    with op.batch_alter_table("student_subject_selections") as batch:
        batch.alter_column("import_batch_id", existing_type=sa.String(length=64), nullable=False)
    with op.batch_alter_table("student_academic_profiles") as batch:
        batch.alter_column("import_batch_id", existing_type=sa.String(length=64), nullable=False)
