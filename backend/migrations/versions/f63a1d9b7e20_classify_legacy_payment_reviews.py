"""classify legacy payment reconciliation work

Revision ID: f63a1d9b7e20
Revises: e42b6c91a730
"""

from alembic import op
import sqlalchemy as sa


revision = "f63a1d9b7e20"
down_revision = "e42b6c91a730"
branch_labels = None
depends_on = None


def upgrade():
    # Incentives are historical notes, not money received. Preserve their
    # immutable source amount while explicitly excluding them from the ledger.
    op.execute(
        sa.text(
            """
            UPDATE payment_transactions
               SET reconciliation_status = 'do_not_import',
                   notes = CASE
                       WHEN TRIM(COALESCE(notes, '')) = ''
                       THEN 'Historical incentive note; excluded from fee receipts.'
                       ELSE notes
                   END
             WHERE status = 'staged'
               AND transaction_type = 'incentive_review'
               AND reconciliation_status <> 'ready'
            """
        )
    )

    # The source workbook genuinely omits these values. Classify the exact
    # missing field instead of leaving a vague generic review state. No date or
    # payment mode is inferred by this migration.
    op.execute(
        sa.text(
            """
            UPDATE payment_transactions
               SET reconciliation_status = CASE
                       WHEN transaction_date IS NULL THEN 'needs_date'
                       WHEN method NOT IN ('cash', 'upi', 'bank_transfer', 'cheque', 'card', 'other')
                           THEN 'needs_mode'
                       ELSE reconciliation_status
                   END,
                   notes = CASE
                       WHEN TRIM(COALESCE(notes, '')) <> '' THEN notes
                       WHEN transaction_date IS NULL
                           THEN 'Payment date was not present in the source workbook; client confirmation required.'
                       WHEN method NOT IN ('cash', 'upi', 'bank_transfer', 'cheque', 'card', 'other')
                           THEN 'Payment mode was not present in the source workbook; client confirmation required.'
                       ELSE notes
                   END
             WHERE status = 'staged'
               AND transaction_type = 'payment'
               AND reconciliation_status = 'review'
            """
        )
    )


def downgrade():
    op.execute(
        sa.text(
            """
            UPDATE payment_transactions
               SET reconciliation_status = 'review',
                   notes = CASE
                       WHEN notes IN (
                           'Payment date was not present in the source workbook; client confirmation required.',
                           'Payment mode was not present in the source workbook; client confirmation required.'
                       ) THEN ''
                       ELSE notes
                   END
             WHERE reconciliation_status IN ('needs_date', 'needs_mode')
            """
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE payment_transactions
               SET reconciliation_status = 'review',
                   notes = CASE
                       WHEN notes = 'Historical incentive note; excluded from fee receipts.' THEN ''
                       ELSE notes
                   END
             WHERE transaction_type = 'incentive_review'
               AND reconciliation_status = 'do_not_import'
            """
        )
    )
