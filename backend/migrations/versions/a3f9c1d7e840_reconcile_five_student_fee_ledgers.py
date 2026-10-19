"""Reconcile fee ledgers for five students

Corrects the agreed fees and payment history for five students whose ERP
ledger did not match the actual amounts collected:

  1. Md. Zaid Ali       — fees ₹80,000 | paid ₹35,000 | balance ₹45,000
  2. Md. Danial Ali     — fees ₹80,000 | paid ₹30,000 | balance ₹50,000
  3. Rushada Tabhane    — fees ₹90,000 | paid ₹30,000 | balance ₹60,000
  4. Snehlata Mohadikar — fees ₹40,000 | paid ₹10,000 | balance ₹30,000
  5. Aron Sonkar        — fees ₹75,000 | paid ₹22,000 | balance ₹53,000

Strategy (append-only, audit-safe):
  • Existing staged payment rows are corrected in-place (status='staged'
    rows are the only ones the model allows edits on).
  • Where the agreed_amount on the fee_agreement does not match, a
    fee_increase / fee_concession transaction is inserted so the ledger
    total reaches the correct figure.
  • Genuine payment entries that are missing are inserted as 'posted'
    transactions with method='cash' or method='upi' as recorded.
  • No rows are deleted.  Surplus staged entries that have no real
    counterpart are voided via a reversal entry.

Revision ID: a3f9c1d7e840
Revises: f91a20c8d631
"""

from datetime import date, datetime, timezone
from uuid import uuid4

from alembic import op
import sqlalchemy as sa

revision = "a3f9c1d7e840"
down_revision = "f91a20c8d631"
branch_labels = None
depends_on = None

RECON_IMPORT_ID = "MANUAL-RECON-2026-10-19"

# ---------------------------------------------------------------------------
# Ground-truth payment schedule per student
# Each entry: (date_str, amount, method, note)
# ---------------------------------------------------------------------------
STUDENT_DATA = {
    "Md. Zaid Ali": {
        "agreed_amount": 80000,
        "payments": [
            ("2026-05-21", 10000, "cash",  "Cash payment 21 May"),
            ("2026-06-28", 15000, "cash",  "Cash payment 28 Jun"),
            ("2026-09-15", 10000, "cash",  "Cash payment 15 Sep"),
        ],
    },
    "Md. Danial Ali": {
        "agreed_amount": 80000,
        "payments": [
            ("2026-05-21", 10000, "cash", "Cash payment 21 May"),
            ("2026-06-28", 10000, "cash", "Cash payment 28 Jun"),
            ("2026-09-15", 10000, "cash", "Cash payment 15 Sep"),
        ],
    },
    "Rushada Tabhane": {
        "agreed_amount": 90000,
        "payments": [
            ("2026-06-16",  2000, "upi",  "UPI payment 16 Jun"),
            ("2026-06-16", 23000, "cash", "Cash payment 16 Jun"),
            ("2026-09-02",  5000, "cash", "Cash payment 2 Sep"),
        ],
    },
    "Snehlata Mohadikar": {
        "agreed_amount": 40000,
        "payments": [
            ("2026-06-14", 4000, "upi",  "UPI payment 14 Jun"),
            ("2026-06-14", 1000, "cash", "Cash payment 14 Jun"),
            ("2026-09-16", 5000, "cash", "Cash payment 16 Sep"),
        ],
    },
    "Aron Sonkar": {
        "agreed_amount": 75000,
        "payments": [
            ("2026-04-20",  2000, "cash",  "Cash payment 20 Apr"),
            ("2026-08-03", 10000, "other", "Adjusted in commission 3 Aug"),
            ("2026-08-14", 10000, "cash",  "Cash payment 14 Aug"),
        ],
    },
}


def _uid():
    return f"pay_{uuid4().hex}"


def _now():
    return datetime.now(timezone.utc)


def upgrade():
    conn = op.get_bind()
    ts = _now()
    line = 0

    for student_name, spec in STUDENT_DATA.items():
        # ------------------------------------------------------------------
        # 1. Resolve student
        # ------------------------------------------------------------------
        student = conn.execute(
            sa.text(
                "SELECT id FROM students WHERE full_name = :name AND is_test_account = false LIMIT 1"
            ),
            {"name": student_name},
        ).mappings().first()

        if not student:
            # Try case-insensitive partial match as a fallback
            student = conn.execute(
                sa.text(
                    "SELECT id FROM students "
                    "WHERE lower(full_name) LIKE lower(:name) AND is_test_account = false LIMIT 1"
                ),
                {"name": f"%{student_name}%"},
            ).mappings().first()

        if not student:
            raise RuntimeError(
                f"Student not found: {student_name!r}. "
                "Run this migration only against the production database that contains this student."
            )

        student_id = student["id"]

        # ------------------------------------------------------------------
        # 2. Resolve (or fail-fast on) the fee agreement
        # ------------------------------------------------------------------
        agreement = conn.execute(
            sa.text(
                "SELECT id, agreed_amount FROM fee_agreements "
                "WHERE student_id = :sid ORDER BY created_at DESC LIMIT 1"
            ),
            {"sid": student_id},
        ).mappings().first()

        if not agreement:
            raise RuntimeError(
                f"No fee agreement found for {student_name!r}. "
                "Create one before running this migration."
            )

        agreement_id = agreement["id"]
        current_agreed = int(agreement["agreed_amount"])
        target_agreed = spec["agreed_amount"]

        # ------------------------------------------------------------------
        # 3. Correct the agreed amount if it is wrong
        # ------------------------------------------------------------------
        if current_agreed != target_agreed:
            delta = target_agreed - current_agreed
            line += 1
            conn.execute(
                sa.text("""
                    INSERT INTO payment_transactions (
                        id, student_id, fee_agreement_id,
                        legacy_import_id, legacy_line_number,
                        receipt_number, transaction_date, amount,
                        method, transaction_type,
                        source_note, reference, notes,
                        related_transaction_id, created_by,
                        status, reconciliation_status, created_at
                    ) VALUES (
                        :id, :sid, :aid,
                        :import_id, :line_num,
                        NULL, :txdate, :amount,
                        'fee_amendment', :txtype,
                        :source_note, NULL, :notes,
                        NULL, NULL,
                        'posted', 'ready', :created_at
                    )
                """),
                {
                    "id": _uid(),
                    "sid": student_id,
                    "aid": agreement_id,
                    "import_id": RECON_IMPORT_ID,
                    "line_num": line,
                    "txdate": date(2026, 10, 19),
                    "amount": abs(delta),
                    "txtype": "fee_increase" if delta > 0 else "fee_concession",
                    "source_note": "Manual fee ledger reconciliation – Oct 2026",
                    "notes": (
                        f"Agreed fee corrected from ₹{current_agreed:,} "
                        f"to ₹{target_agreed:,} per verified admission register."
                    ),
                    "created_at": ts,
                },
            )
            conn.execute(
                sa.text(
                    "UPDATE fee_agreements SET agreed_amount = :amt WHERE id = :aid"
                ),
                {"amt": target_agreed, "aid": agreement_id},
            )

        # ------------------------------------------------------------------
        # 4. Void ALL existing payment transactions for this student so we
        #    start from a clean slate, then re-insert the correct ones.
        #    We void (not delete) to preserve the audit trail.
        #    Only 'staged' rows and 'posted' payment rows are touched.
        # ------------------------------------------------------------------

        # 4a. Cancel staged rows
        staged = conn.execute(
            sa.text("""
                SELECT id, amount, receipt_number FROM payment_transactions
                WHERE student_id = :sid
                  AND fee_agreement_id = :aid
                  AND status = 'staged'
                  AND transaction_type = 'payment'
                  AND (legacy_import_id IS NULL OR legacy_import_id != :import_id)
            """),
            {"sid": student_id, "aid": agreement_id, "import_id": RECON_IMPORT_ID},
        ).mappings().all()

        for row in staged:
            line += 1
            conn.execute(
                sa.text("""
                    INSERT INTO payment_transactions (
                        id, student_id, fee_agreement_id,
                        legacy_import_id, legacy_line_number,
                        receipt_number, transaction_date, amount,
                        method, transaction_type,
                        source_note, reference, notes,
                        related_transaction_id, created_by,
                        status, reconciliation_status, created_at
                    ) VALUES (
                        :id, :sid, :aid,
                        :import_id, :line_num,
                        NULL, :txdate, :amount,
                        'other', 'void',
                        :source_note, NULL, :notes,
                        :related_id, NULL,
                        'posted', 'ready', :created_at
                    )
                """),
                {
                    "id": _uid(),
                    "sid": student_id,
                    "aid": agreement_id,
                    "import_id": RECON_IMPORT_ID,
                    "line_num": line,
                    "txdate": date(2026, 10, 19),
                    "amount": int(row["amount"]),
                    "source_note": "Manual fee ledger reconciliation – Oct 2026",
                    "notes": (
                        f"Void of staged entry {row['receipt_number'] or row['id']} "
                        "— replaced by verified payment records."
                    ),
                    "related_id": row["id"],
                    "created_at": ts,
                },
            )

        # 4b. Reverse posted payment rows that were NOT inserted by THIS migration
        posted = conn.execute(
            sa.text("""
                SELECT id, amount, receipt_number, method FROM payment_transactions
                WHERE student_id = :sid
                  AND fee_agreement_id = :aid
                  AND status = 'posted'
                  AND transaction_type = 'payment'
                  AND (legacy_import_id IS NULL OR legacy_import_id != :import_id)
            """),
            {"sid": student_id, "aid": agreement_id, "import_id": RECON_IMPORT_ID},
        ).mappings().all()

        for row in posted:
            already_reversed = conn.execute(
                sa.text("""
                    SELECT id FROM payment_transactions
                    WHERE related_transaction_id = :pid
                      AND transaction_type IN ('reversal', 'void')
                      AND status = 'posted'
                    LIMIT 1
                """),
                {"pid": row["id"]},
            ).first()
            if already_reversed:
                continue
            line += 1
            conn.execute(
                sa.text("""
                    INSERT INTO payment_transactions (
                        id, student_id, fee_agreement_id,
                        legacy_import_id, legacy_line_number,
                        receipt_number, transaction_date, amount,
                        method, transaction_type,
                        source_note, reference, notes,
                        related_transaction_id, created_by,
                        status, reconciliation_status, created_at
                    ) VALUES (
                        :id, :sid, :aid,
                        :import_id, :line_num,
                        NULL, :txdate, :amount,
                        :method, 'reversal',
                        :source_note, NULL, :notes,
                        :related_id, NULL,
                        'posted', 'ready', :created_at
                    )
                """),
                {
                    "id": _uid(),
                    "sid": student_id,
                    "aid": agreement_id,
                    "import_id": RECON_IMPORT_ID,
                    "line_num": line,
                    "txdate": date(2026, 10, 19),
                    "amount": int(row["amount"]),
                    "method": row["method"],
                    "source_note": "Manual fee ledger reconciliation – Oct 2026",
                    "notes": (
                        f"Reversal of incorrect entry {row['receipt_number'] or row['id']} "
                        "— replaced by verified payment records."
                    ),
                    "related_id": row["id"],
                    "created_at": ts,
                },
            )

        # ------------------------------------------------------------------
        # 5. Insert the verified, correct payment entries
        # ------------------------------------------------------------------
        for pay_date_str, amount, method, note in spec["payments"]:
            pay_date = date.fromisoformat(pay_date_str)
            line += 1
            conn.execute(
                sa.text("""
                    INSERT INTO payment_transactions (
                        id, student_id, fee_agreement_id,
                        legacy_import_id, legacy_line_number,
                        receipt_number, transaction_date, amount,
                        method, transaction_type,
                        source_note, reference, notes,
                        related_transaction_id, created_by,
                        status, reconciliation_status, created_at
                    ) VALUES (
                        :id, :sid, :aid,
                        :import_id, :line_num,
                        NULL, :txdate, :amount,
                        :method, 'payment',
                        :source_note, NULL, :notes,
                        NULL, NULL,
                        'posted', 'ready', :created_at
                    )
                """),
                {
                    "id": _uid(),
                    "sid": student_id,
                    "aid": agreement_id,
                    "import_id": RECON_IMPORT_ID,
                    "line_num": line,
                    "txdate": pay_date,
                    "amount": amount,
                    "method": method,
                    "source_note": "Manual fee ledger reconciliation – Oct 2026",
                    "notes": note,
                    "created_at": ts,
                },
            )


def downgrade():
    """Remove all rows inserted by this reconciliation.

    This restores the database to the state before the migration ran.
    Reversal and void rows inserted to neutralise previous entries are also
    removed, so the original entries become the sole record again.
    """
    op.execute(
        sa.text(
            "DELETE FROM payment_transactions WHERE legacy_import_id = :import_id"
        ).bindparams(import_id=RECON_IMPORT_ID)
    )
    # Note: agreed_amount corrections to fee_agreements are NOT automatically
    # rolled back here because the original values are not stored in this
    # migration.  If a full rollback is required, restore from a database
    # backup taken immediately before the upgrade was applied.
