import json
from pathlib import Path

import pytest

from app.importers.legacy_admissions import import_manifest
from app.models import Enrollment, FeeAgreement, ImportBatch, LegacyAdmissionRow, PaymentTransaction, Student

MANIFEST = Path(__file__).parents[1] / "data" / "imports" / "admission_2026_27.json"
pytestmark = pytest.mark.skipif(
    not MANIFEST.exists(),
    reason="Private admission manifest is intentionally excluded from the repository",
)


def load_manifest():
    return json.loads(MANIFEST.read_text())


def test_full_workbook_import_reconciles_and_is_idempotent(database):
    first = import_manifest(database, load_manifest())
    second = import_manifest(database, load_manifest())
    assert first == {
        "batch_id": first["batch_id"],
        "idempotent_rerun": False,
        "active_rows": 64,
        "cancelled_rows": 6,
        "students": 64,
        "enrollments": 64,
        "fee_agreements": 64,
        "agreed_fee_total": 4_227_000,
        "registration_total": 830_100,
        "staged_payment_lines": 115,
        "staged_payment_total": 819_100,
        "adjustment_review_lines": 3,
    }
    assert second["batch_id"] == first["batch_id"]
    assert second["idempotent_rerun"] is True
    assert database.query(ImportBatch).count() == 1
    assert database.query(Student).count() == 64


def test_source_fields_are_preserved_without_inventing_missing_data(database):
    import_manifest(database, load_manifest())
    kamal = database.query(Student).filter_by(legacy_import_id="LEGACY-ADM-2026-A-001").one()
    assert (kamal.full_name, kamal.mobile, kamal.secondary_mobile, kamal.previous_school) == (
        "Kamal Parsatwar", "9158978800", "9158178887", "Podar International School"
    )
    enrollment = database.query(Enrollment).filter_by(student_id=kamal.id).one()
    fee = database.query(FeeAgreement).filter_by(student_id=kamal.id).one()
    assert enrollment.enrollment_date.isoformat() == "2026-01-21"
    assert enrollment.program == "JEE"
    assert (fee.agreed_amount, fee.legacy_registration_total) == (110_000, 30_000)

    nancy = database.query(Student).filter_by(legacy_import_id="LEGACY-ADM-2026-A-003").one()
    assert nancy.mobile is None
    assert nancy.data_quality_status == "blocked"
    assert database.query(LegacyAdmissionRow).filter_by(record_status="cancelled").count() == 6
    assert database.query(Student).filter(Student.legacy_import_id.like("%-C-%")).count() == 0


def test_imported_payment_lines_are_immutable(database):
    import_manifest(database, load_manifest())
    payment = database.query(PaymentTransaction).first()
    payment.amount += 1
    with pytest.raises(ValueError, match="immutable"):
        database.flush()
    database.rollback()


def test_imported_records_are_available_through_protected_apis(client, owner_headers, database):
    import_manifest(database, load_manifest())
    students = client.get("/api/students?pageSize=100", headers=owner_headers)
    agreements = client.get("/api/finance/agreements?pageSize=100", headers=owner_headers)
    payments = client.get("/api/finance/staged-payments?pageSize=100", headers=owner_headers)
    assert students.status_code == agreements.status_code == payments.status_code == 200
    assert students.json()["total"] == 64
    assert agreements.json()["total"] == 64
    assert payments.json()["total"] == 118
