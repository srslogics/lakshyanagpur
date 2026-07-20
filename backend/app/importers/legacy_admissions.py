from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import (
    AuditLog,
    Enrollment,
    FeeAgreement,
    FinanceHandoff,
    ImportBatch,
    LegacyAdmissionRow,
    PaymentTransaction,
    Student,
)


class ImportConflict(ValueError):
    pass


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _validate(manifest: dict) -> None:
    if manifest.get("schema_version") != 1:
        raise ImportConflict("Unsupported admission manifest schema")
    records = manifest.get("records", [])
    active = [row for row in records if row["record_status"] == "active"]
    cancelled = [row for row in records if row["record_status"] == "cancelled"]
    expected = manifest["expected"]
    checks = {
        "active_rows": len(active),
        "cancelled_rows": len(cancelled),
        "fee_total": sum(row["normalized"]["agreed_fee"] for row in active),
        "registration_total": sum(row["normalized"]["registration_total"] for row in active),
        "staged_payment_total": sum(
            payment["amount"]
            for row in active
            for payment in row["payments"]
            if payment["transaction_type"] == "payment"
        ),
    }
    if checks != expected:
        raise ImportConflict(f"Manifest reconciliation failed: expected {expected}, calculated {checks}")
    legacy_ids = [row["legacy_id"] for row in records]
    if len(legacy_ids) != len(set(legacy_ids)):
        raise ImportConflict("Manifest contains duplicate legacy admission IDs")


def import_manifest(db: Session, manifest: dict, actor_id: str | None = None) -> dict:
    _validate(manifest)
    source = manifest["source"]
    expected = manifest["expected"]
    previous = db.query(ImportBatch).filter_by(source_hash=source["sha256"]).first()
    if previous:
        return reconciliation(db, previous.id, idempotent=True)

    batch = ImportBatch(
        source_name=source["name"],
        source_hash=source["sha256"],
        source_sheet=source["sheet"],
        active_rows=expected["active_rows"],
        cancelled_rows=expected["cancelled_rows"],
        fee_total=expected["fee_total"],
        registration_total=expected["registration_total"],
        staged_payment_total=expected["staged_payment_total"],
        actor_id=actor_id,
    )
    db.add(batch)
    db.flush()

    try:
        for row in manifest["records"]:
            existing = db.get(LegacyAdmissionRow, row["legacy_id"])
            if existing:
                if existing.raw_data != row["raw"] or existing.normalized_data != row["normalized"]:
                    raise ImportConflict(f"Legacy row {row['legacy_id']} already exists with different data")
                continue

            legacy = LegacyAdmissionRow(
                id=row["legacy_id"],
                import_batch_id=batch.id,
                source_row=row["source_row"],
                record_status=row["record_status"],
                import_readiness=row["import_readiness"].lower().replace(" ", "_"),
                raw_data=row["raw"],
                normalized_data=row["normalized"],
                issues=row["issues"],
            )
            db.add(legacy)
            if row["record_status"] == "cancelled":
                continue

            data = row["normalized"]
            suffix = row["legacy_id"].rsplit("-", 1)[-1]
            student = Student(
                admission_number=f"LI-2026-L{suffix}",
                full_name=data["student_name"],
                mobile=data["primary_mobile"],
                secondary_mobile=data["secondary_mobile"],
                previous_school=data["previous_school"],
                legacy_import_id=row["legacy_id"],
                data_quality_status=row["import_readiness"].lower(),
                status="active",
            )
            db.add(student)
            db.flush()
            legacy.student_id = student.id

            enrollment = Enrollment(
                student_id=student.id,
                program=data["program"],
                batch=None,
                enrollment_date=_date(data["admission_date"]),
                source_type="legacy_excel_import",
                legacy_import_id=row["legacy_id"],
                status="active",
                is_active=True,
            )
            db.add(enrollment)
            db.flush()
            fee = FeeAgreement(
                student_id=student.id,
                enrollment_id=enrollment.id,
                legacy_import_id=row["legacy_id"],
                agreed_amount=data["agreed_fee"],
                legacy_registration_total=data["registration_total"],
                status="active",
            )
            db.add(fee)
            db.flush()
            db.add(FinanceHandoff(student_id=student.id, enrollment_id=enrollment.id, status="legacy_fee_imported"))

            for payment in row["payments"]:
                db.add(PaymentTransaction(
                    student_id=student.id,
                    fee_agreement_id=fee.id,
                    legacy_import_id=row["legacy_id"],
                    legacy_line_number=payment["line_number"],
                    transaction_date=_date(payment["transaction_date"]),
                    amount=payment["amount"],
                    method=payment["method"],
                    transaction_type=payment["transaction_type"],
                    source_note=payment["source_note"],
                    status="staged",
                    reconciliation_status=payment["reconciliation_status"],
                ))

        db.add(AuditLog(
            actor_id=actor_id,
            action="migration.admissions.import",
            entity_type="import_batch",
            entity_id=batch.id,
            before=None,
            after=expected,
        ))
        db.commit()
    except Exception:
        db.rollback()
        raise
    return reconciliation(db, batch.id)


def reconciliation(db: Session, batch_id: str, idempotent: bool = False) -> dict:
    batch = db.get(ImportBatch, batch_id)
    if not batch:
        raise ImportConflict("Import batch not found")
    legacy_rows = db.query(LegacyAdmissionRow).filter_by(import_batch_id=batch.id)
    active_ids = [row.id for row in legacy_rows.filter_by(record_status="active").all()]
    student_count = db.query(Student).filter(Student.legacy_import_id.in_(active_ids)).count() if active_ids else 0
    fee_rows = db.query(FeeAgreement).filter(FeeAgreement.legacy_import_id.in_(active_ids)) if active_ids else None
    fees = fee_rows.all() if fee_rows is not None else []
    payment_rows = db.query(PaymentTransaction).filter(PaymentTransaction.legacy_import_id.in_(active_ids)).all() if active_ids else []
    return {
        "batch_id": batch.id,
        "idempotent_rerun": idempotent,
        "active_rows": legacy_rows.filter_by(record_status="active").count(),
        "cancelled_rows": legacy_rows.filter_by(record_status="cancelled").count(),
        "students": student_count,
        "enrollments": db.query(Enrollment).filter(Enrollment.legacy_import_id.in_(active_ids)).count() if active_ids else 0,
        "fee_agreements": len(fees),
        "agreed_fee_total": sum(row.agreed_amount for row in fees),
        "registration_total": sum(row.legacy_registration_total for row in fees),
        "staged_payment_lines": sum(1 for row in payment_rows if row.transaction_type == "payment"),
        "staged_payment_total": sum(row.amount for row in payment_rows if row.transaction_type == "payment"),
        "adjustment_review_lines": sum(1 for row in payment_rows if row.transaction_type != "payment"),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Import the reviewed Lakshya admissions manifest")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    _validate(manifest)
    if args.dry_run:
        print(json.dumps({"status": "valid", **manifest["expected"]}, indent=2))
        return
    with SessionLocal() as db:
        print(json.dumps(import_manifest(db, manifest), indent=2))


if __name__ == "__main__":
    main()
