import copy
from datetime import date

import pytest

from app.importers.admission_revision import AdmissionRevisionConflict, import_revision
from app.models import (
    Enrollment,
    FeeAgreement,
    FinanceHandoff,
    PaymentTransaction,
    Student,
    StudentAcademicProfile,
    StudentAccount,
    User,
)
from app.services import payment_effect


def manifest():
    active = []
    cancelled = []
    for index in range(57):
        name = "New Student" if index == 0 else f"Active Student {index:02d}"
        action = "create" if index == 0 else "update"
        baseline_paid = None if index == 0 else 19_100 if index == 56 else 15_000
        registration_total = 5_000 if index == 0 else baseline_paid
        agreed_fee = 40_000 if index == 0 else 69_500 if index == 56 else 68_500
        active.append({
            "sourceRow": index + 3,
            "recordStatus": "active",
            "originalLegacyId": None if action == "create" else f"OLD-A-{index}",
            "action": action,
            "raw": {"studentName": name},
            "normalized": {
                "admissionDate": "2026-08-04",
                "studentName": name,
                "previousSchool": "School",
                "primaryMobile": "9876543210" if action == "create" else f"900000{index:04d}",
                "secondaryMobile": None,
                "program": "MHT-CET",
                "admissionLeadRaw": "Client",
                "agreedFee": agreed_fee,
                "registrationTotal": registration_total,
                "baselinePaid": baseline_paid,
            },
            "payments": [{
                "lineNumber": 1,
                "transactionDate": "2026-08-04",
                "amount": 5_000,
                "method": "upi",
                "transactionType": "payment",
                "sourceNote": "5k UPI 4-8",
            }] if action == "create" else [],
            "issues": [],
        })
    for index in range(13):
        name = "Cancelled Student" if index == 0 else f"Historical Cancelled {index:02d}"
        cancelled.append({
            "sourceRow": 63 + index,
            "recordStatus": "cancelled",
            "originalLegacyId": f"OLD-C-{index}",
            "action": "status_change" if index < 7 else "update",
            "raw": {"studentName": name},
            "normalized": {
                "admissionDate": "2026-01-01",
                "studentName": name,
                "previousSchool": "School",
                "primaryMobile": f"800000{index:04d}",
                "secondaryMobile": None,
                "program": "Boards",
                "admissionLeadRaw": "Client",
                "agreedFee": 40_000,
                "registrationTotal": 1_000,
                "baselinePaid": 1_000,
            },
            "payments": [],
            "issues": [],
        })
    return {
        "schemaVersion": 1,
        "revisionId": "TEST-ADMISSION-REVISION",
        "effectiveDate": "2026-08-13",
        "paymentCutoff": "2026-08-03",
        "source": {"sheet": "Admission", "contentSha256": "test", "files": [], "identicalCopies": 2},
        "baseline": {"snapshotId": "TEST", "source": "test"},
        "controls": {
            "activeRows": 57,
            "cancelledRows": 13,
            "studentRows": 70,
            "activeFeeTotal": 3_877_000,
            "activeRegistrationTotal": 849_100,
            "explicitStatusChanges": 7,
            "newActiveStudents": 1,
            "retainedMissingStudents": 1,
        },
        "records": active + cancelled,
        "retainedMissingRecords": [{
            "studentName": "Retained Student",
            "originalLegacyId": "OLD-RETAINED",
            "reason": "No cancellation is recorded",
        }],
    }


def add_existing_student(db, name, *, status="active", agreed=68_160, paid=1_000):
    serial = db.query(Student).count() + 1
    student = Student(
        admission_number=f"LI-2026-{serial:05d}",
        full_name=name,
        mobile=None,
        status=status,
        data_quality_status="ready",
    )
    db.add(student); db.flush()
    enrollment = Enrollment(
        student_id=student.id,
        program="MHT-CET",
        batch="Essential",
        enrollment_date=date(2026, 1, 1),
        status=status,
        is_active=status == "active",
    )
    db.add(enrollment); db.flush()
    db.add(StudentAcademicProfile(
        student_id=student.id,
        source_student_code=f"TEST-{serial}",
        batch_name="Essential",
        source_stream="MHT-CET",
    ))
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        agreed_amount=agreed,
        legacy_registration_total=paid,
        status="active" if status == "active" else "inactive",
    )
    db.add(agreement); db.flush()
    db.add(FinanceHandoff(student_id=student.id, enrollment_id=enrollment.id))
    if paid:
        db.add(PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            transaction_date=date(2026, 8, 3),
            amount=paid,
            method="client_statement",
            transaction_type="balance_credit",
            source_note="baseline",
            status="posted",
            reconciliation_status="ready",
        ))
    return student


def seed_manifest_students(db, payload):
    for row in payload["records"]:
        if row["action"] == "create":
            continue
        add_existing_student(
            db,
            row["normalized"]["studentName"],
            status="active" if row["action"] == "status_change" else "forfeited" if row["recordStatus"] == "cancelled" else "active",
            agreed=row["normalized"]["agreedFee"],
            paid=row["normalized"]["baselinePaid"],
        )
    add_existing_student(db, "Retained Student", agreed=40_000, paid=5_000)
    db.commit()


def test_revision_preview_apply_and_idempotency(database):
    payload = manifest()
    seed_manifest_students(database, payload)
    owner = database.query(User).filter_by(role="owner").one()

    preview = import_revision(database, payload, owner, apply=False)
    assert preview["applied"] is False
    assert [row["name"] for row in preview["newStudents"]] == ["New Student"]
    assert len(preview["statusChanges"]) == 7
    assert preview["statusChanges"][0]["name"] == "Cancelled Student"
    assert any(row["name"] == "Retained Student" for row in preview["reviewRequired"])

    result = import_revision(database, payload, owner, apply=True)
    assert result["applied"] is True
    new_student = database.query(Student).filter_by(full_name="New Student").one()
    assert new_student.status == "active"
    assert database.query(StudentAccount).filter_by(student_id=new_student.id).count() == 1
    new_agreement = database.query(FeeAgreement).filter_by(student_id=new_student.id).one()
    assert sum(payment_effect(row) for row in database.query(PaymentTransaction).filter_by(fee_agreement_id=new_agreement.id)) == 5_000

    cancelled = database.query(Student).filter_by(full_name="Cancelled Student").one()
    assert cancelled.status == "forfeited"
    cancelled_agreement = database.query(FeeAgreement).filter_by(student_id=cancelled.id).one()
    assert cancelled_agreement.status == "inactive"
    assert sum(payment_effect(row) for row in database.query(PaymentTransaction).filter_by(fee_agreement_id=cancelled_agreement.id)) == cancelled_agreement.agreed_amount

    rerun = import_revision(database, payload, owner, apply=True)
    assert rerun["alreadyApplied"] is True
    assert database.query(Student).filter_by(full_name="New Student").count() == 1


def test_revision_rejects_changed_controls(database):
    payload = copy.deepcopy(manifest())
    payload["controls"]["activeRows"] = 58
    owner = database.query(User).filter_by(role="owner").one()
    with pytest.raises(AdmissionRevisionConflict):
        import_revision(database, payload, owner, apply=False)


def test_revision_matches_renamed_student_by_legacy_id(database):
    payload = manifest()
    seed_manifest_students(database, payload)
    row = payload["records"][1]
    student = database.query(Student).filter_by(
        full_name=row["normalized"]["studentName"]
    ).one()
    student.full_name = "Nancy Magare (corrected)"
    student.legacy_import_id = row["originalLegacyId"]
    database.commit()

    owner = database.query(User).filter_by(role="owner").one()
    preview = import_revision(database, payload, owner, apply=False)

    assert preview["applied"] is False
    assert preview["alreadyApplied"] is False
