"""reconcile receipts entered after a client balance snapshot

Revision ID: d2e8f4a1c630
Revises: c8a17f4d9e20
"""

from datetime import datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


revision = "d2e8f4a1c630"
down_revision = "c8a17f4d9e20"
branch_labels = None
depends_on = None

REPAIR_IMPORT_ID = "BACKDATED-RECON-2026-08-18"


def upgrade():
    connection = op.get_bind()
    payments = connection.execute(sa.text("""
        SELECT id, student_id, fee_agreement_id, receipt_number,
               transaction_date, amount, created_at
          FROM payment_transactions
         WHERE transaction_type = 'payment'
           AND status IN ('staged', 'posted')
           AND reconciliation_status = 'ready'
           AND transaction_date IS NOT NULL
         ORDER BY created_at, id
    """)).mappings().all()

    repair_line = 0
    for payment in payments:
        already_repaired = connection.execute(sa.text("""
            SELECT id
              FROM payment_transactions
             WHERE related_transaction_id = :payment_id
               AND transaction_type = 'balance_debit'
               AND method = 'client_statement'
               AND status = 'posted'
             LIMIT 1
        """), {"payment_id": payment["id"]}).first()
        if already_repaired:
            continue

        snapshot = connection.execute(sa.text("""
            SELECT id, transaction_date, reference, created_at
              FROM payment_transactions
             WHERE fee_agreement_id = :agreement_id
               AND method = 'client_statement'
               AND transaction_type IN ('balance_credit', 'balance_debit')
               AND status = 'posted'
               AND reconciliation_status = 'ready'
               AND transaction_date >= :payment_date
               AND created_at < :payment_created_at
             ORDER BY transaction_date DESC, created_at DESC, id DESC
             LIMIT 1
        """), {
            "agreement_id": payment["fee_agreement_id"],
            "payment_date": payment["transaction_date"],
            "payment_created_at": payment["created_at"],
        }).mappings().first()
        if not snapshot:
            continue

        repair_line += 1
        connection.execute(sa.text("""
            INSERT INTO payment_transactions (
                id, student_id, fee_agreement_id, legacy_import_id,
                legacy_line_number, receipt_number, transaction_date, amount,
                method, transaction_type, source_note, reference, notes,
                related_transaction_id, created_by, status,
                reconciliation_status, created_at
            ) VALUES (
                :id, :student_id, :agreement_id, :legacy_import_id,
                :legacy_line_number, NULL, :transaction_date, :amount,
                'client_statement', 'balance_debit', :source_note, :reference,
                :notes, :related_transaction_id, NULL, 'posted', 'ready',
                :created_at
            )
        """), {
            "id": f"pay_{uuid4().hex}",
            "student_id": payment["student_id"],
            "agreement_id": payment["fee_agreement_id"],
            "legacy_import_id": REPAIR_IMPORT_ID,
            "legacy_line_number": repair_line,
            "transaction_date": snapshot["transaction_date"],
            "amount": payment["amount"],
            "source_note": "Backdated receipt already included in confirmed balance",
            "reference": snapshot["reference"],
            "notes": (
                f"Offsets {payment['receipt_number'] or payment['id']} for ledger balance only; "
                "the receipt remains included in money received."
            ),
            "related_transaction_id": payment["id"],
            "created_at": datetime.now(timezone.utc),
        })


def downgrade():
    op.execute(
        sa.text("DELETE FROM payment_transactions WHERE legacy_import_id = :import_id")
        .bindparams(import_id=REPAIR_IMPORT_ID)
    )
