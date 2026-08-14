from __future__ import annotations

import os
import re
from datetime import date

from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from ..models import (
    AuditLog,
    Enrollment,
    FeeAgreement,
    FinanceHandoff,
    PaymentTransaction,
    Student,
    StudentAcademicProfile,
    StudentAccount,
    User,
)
from ..routers.students import _apply_student_lifecycle
from ..security import hash_password
from ..services import admission_number, canonical_program, payment_effect


class AdmissionRevisionConflict(ValueError):
    pass


def _name_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _validate(manifest: dict) -> None:
    if manifest.get("schemaVersion") != 1:
        raise AdmissionRevisionConflict("Unsupported admission revision schema")
    records = manifest.get("records", [])
    active = [row for row in records if row.get("recordStatus") == "active"]
    cancelled = [row for row in records if row.get("recordStatus") == "cancelled"]
    controls = manifest.get("controls", {})
    calculated = {
        "activeRows": len(active),
        "cancelledRows": len(cancelled),
        "studentRows": len(records),
        "activeFeeTotal": sum(int(row["normalized"]["agreedFee"]) for row in active),
        "activeRegistrationTotal": sum(int(row["normalized"]["registrationTotal"]) for row in active),
        "explicitStatusChanges": sum(row.get("action") == "status_change" for row in records),
        "newActiveStudents": sum(
            row.get("action") == "create" and row.get("recordStatus") == "active"
            for row in records
        ),
        "retainedMissingStudents": len(manifest.get("retainedMissingRecords", [])),
    }
    if controls != calculated:
        raise AdmissionRevisionConflict(
            f"Admission revision controls do not reconcile: {calculated}"
        )
    keys = [_name_key(row["normalized"]["studentName"]) for row in records]
    if len(keys) != len(set(keys)):
        raise AdmissionRevisionConflict("Admission revision contains duplicate student names")
    if controls != {
        "activeRows": 57,
        "cancelledRows": 13,
        "studentRows": 70,
        "activeFeeTotal": 3_877_000,
        "activeRegistrationTotal": 849_100,
        "explicitStatusChanges": 7,
        "newActiveStudents": 1,
        "retainedMissingStudents": 1,
    }:
        raise AdmissionRevisionConflict("Admission revision does not match the client control totals")


def _student_indexes(db: Session) -> tuple[dict[str, Student], dict[str, Student]]:
    by_name: dict[str, Student] = {}
    by_legacy_id: dict[str, Student] = {}
    for student in db.query(Student).filter(Student.is_test_account.is_(False)).all():
        key = _name_key(student.full_name)
        if key in by_name:
            raise AdmissionRevisionConflict(
                f"More than one student matches the name {student.full_name}"
            )
        by_name[key] = student
        if student.legacy_import_id:
            by_legacy_id[student.legacy_import_id] = student
    return by_name, by_legacy_id


def _match_student(
    row: dict,
    by_name: dict[str, Student],
    by_legacy_id: dict[str, Student],
) -> Student | None:
    # The legacy admission ID is immutable. Names can be corrected by the owner,
    # so only use the normalized name as a fallback for older/manual records.
    legacy_id = row.get("originalLegacyId")
    if legacy_id and legacy_id in by_legacy_id:
        return by_legacy_id[legacy_id]
    return by_name.get(_name_key(row["normalized"]["studentName"]))


def _agreement(db: Session, student: Student) -> FeeAgreement:
    agreement = (
        db.query(FeeAgreement)
        .filter_by(student_id=student.id)
        .order_by(FeeAgreement.created_at.desc(), FeeAgreement.id.desc())
        .first()
    )
    if not agreement:
        raise AdmissionRevisionConflict(f"Fee agreement not found for {student.full_name}")
    return agreement


def _current_paid(db: Session, agreement: FeeAgreement) -> int:
    transactions = db.query(PaymentTransaction).filter_by(
        fee_agreement_id=agreement.id
    ).all()
    return sum(payment_effect(row) for row in transactions)


def _new_payments(row: dict, cutoff: str) -> list[dict]:
    return [
        payment
        for payment in row.get("payments", [])
        if payment.get("transactionType") == "payment"
        and payment.get("transactionDate")
        and payment["transactionDate"] > cutoff
    ]


def _preview(db: Session, manifest: dict) -> dict:
    _validate(manifest)
    by_name, by_legacy_id = _student_indexes(db)
    revision_id = manifest["revisionId"]
    already_applied = db.query(AuditLog).filter_by(
        action="admission.revision.import",
        entity_type="admission_revision",
        entity_id=revision_id,
    ).first()
    if already_applied:
        return {
            "revisionId": revision_id,
            "alreadyApplied": True,
            "applied": False,
            "controls": manifest["controls"],
            "newStudents": [],
            "statusChanges": [],
            "payments": [],
            "reviewRequired": [],
            "retainedMissingStudents": manifest.get("retainedMissingRecords", []),
        }

    new_students = []
    status_changes = []
    payments = []
    review_required = []
    cutoff = manifest["paymentCutoff"]
    for row in manifest["records"]:
        data = row["normalized"]
        student = _match_student(row, by_name, by_legacy_id)
        if row["action"] == "create":
            if student:
                raise AdmissionRevisionConflict(
                    f"New admission already matches {student.full_name}"
                )
            new_students.append({
                "name": data["studentName"],
                "mobile": data["primaryMobile"],
                "program": data["program"],
                "agreedFee": data["agreedFee"],
                "paid": data["registrationTotal"],
            })
            continue
        if not student:
            raise AdmissionRevisionConflict(f"Student not found: {data['studentName']}")
        if row["action"] == "status_change" and row["recordStatus"] == "cancelled":
            if student.status != "forfeited":
                status_changes.append({"name": student.full_name, "to": "forfeited"})
        if row["recordStatus"] != "active":
            if row.get("issues"):
                review_required.append({"name": student.full_name, "issues": row["issues"]})
            continue
        agreement = _agreement(db, student)
        if agreement.agreed_amount != int(data["agreedFee"]):
            raise AdmissionRevisionConflict(
                f"Agreed fee changed for {student.full_name}; review it in Finance before import"
            )
        latest = _new_payments(row, cutoff)
        expected_delta = int(data["registrationTotal"]) - int(data["baselinePaid"] or 0)
        latest_total = sum(int(payment["amount"] or 0) for payment in latest)
        current_paid = _current_paid(db, agreement)
        if expected_delta != latest_total:
            review_required.append({
                "name": student.full_name,
                "issues": [
                    *row.get("issues", []),
                    "Paid-total change does not reconcile to dated post-cutoff payments",
                ],
            })
            continue
        if current_paid not in {int(data["baselinePaid"] or 0), int(data["registrationTotal"])}:
            raise AdmissionRevisionConflict(
                f"Current ledger total for {student.full_name} is ₹{current_paid:,}; "
                f"expected either the 3 August baseline ₹{int(data['baselinePaid'] or 0):,} "
                f"or the revised total ₹{int(data['registrationTotal']):,}"
            )
        if current_paid == int(data["baselinePaid"] or 0):
            payments.extend({
                "name": student.full_name,
                "date": payment["transactionDate"],
                "amount": int(payment["amount"]),
                "method": payment["method"],
                "sourceNote": payment["sourceNote"],
            } for payment in latest)
        if row.get("issues"):
            review_required.append({"name": student.full_name, "issues": row["issues"]})

    for retained in manifest.get("retainedMissingRecords", []):
        student = by_legacy_id.get(retained.get("originalLegacyId"))
        if not student:
            student = by_name.get(_name_key(retained["studentName"]))
        if not student:
            raise AdmissionRevisionConflict(
                f"Retained student not found: {retained['studentName']}"
            )
        review_required.append({
            "name": student.full_name,
            "issues": [retained["reason"]],
        })

    return {
        "revisionId": revision_id,
        "alreadyApplied": False,
        "applied": False,
        "controls": manifest["controls"],
        "newStudents": new_students,
        "statusChanges": status_changes,
        "payments": payments,
        "reviewRequired": review_required,
        "retainedMissingStudents": manifest.get("retainedMissingRecords", []),
    }


def _create_student(db: Session, row: dict, actor: User, revision_id: str) -> Student:
    data = row["normalized"]
    if not data["primaryMobile"]:
        raise AdmissionRevisionConflict(f"Mobile is required for {data['studentName']}")
    if db.query(User).filter_by(mobile=data["primaryMobile"]).first():
        raise AdmissionRevisionConflict(
            f"Mobile {data['primaryMobile']} already belongs to a portal account"
        )
    student = Student(
        admission_number=admission_number(db),
        full_name=data["studentName"],
        mobile=data["primaryMobile"],
        secondary_mobile=data["secondaryMobile"],
        previous_school=data["previousSchool"],
        legacy_import_id=None,
        data_quality_status="review" if row.get("issues") else "ready",
        status="active",
    )
    db.add(student)
    db.flush()
    program = canonical_program(data["program"])
    batch = "Essential" if program in {"MHT-CET", "Boards"} else "Tatva"
    enrollment = Enrollment(
        student_id=student.id,
        program=program,
        batch=batch,
        enrollment_date=_date(data["admissionDate"]),
        source_type="client_admission_revision",
        status="active",
        is_active=True,
    )
    db.add(enrollment)
    db.flush()
    db.add(StudentAcademicProfile(
        student_id=student.id,
        source_student_code=f"ERP-{student.admission_number}",
        batch_name=batch,
        source_stream=program,
        mentor_name=None,
        source_school_name=student.previous_school,
        source_primary_mobile=student.mobile,
        source_secondary_mobile=student.secondary_mobile,
        import_batch_id=None,
    ))
    agreement = FeeAgreement(
        student_id=student.id,
        enrollment_id=enrollment.id,
        agreed_amount=int(data["agreedFee"]),
        legacy_registration_total=int(data["registrationTotal"]),
        currency="INR",
        status="active",
    )
    db.add(agreement)
    db.flush()
    db.add(FinanceHandoff(
        student_id=student.id,
        enrollment_id=enrollment.id,
        status="client_revision_imported",
    ))
    for index, payment in enumerate(_new_payments(row, "2026-08-03"), 1):
        db.add(PaymentTransaction(
            student_id=student.id,
            fee_agreement_id=agreement.id,
            legacy_import_id=revision_id,
            legacy_line_number=10_000 + index,
            transaction_date=_date(payment["transactionDate"]),
            amount=int(payment["amount"]),
            method=payment["method"],
            transaction_type="payment",
            source_note=payment["sourceNote"],
            reference=manifest_reference(revision_id, row["sourceRow"]),
            notes="Client-confirmed admission register revision.",
            created_by=actor.id,
            status="posted",
            reconciliation_status="ready",
        ))
    temporary_password = os.getenv("PORTAL_SHARED_TEMP_PASSWORD", "Lakshaya@2026")
    account = User(
        mobile=data["primaryMobile"],
        full_name=student.full_name,
        password_hash=hash_password(temporary_password),
        role="student",
        is_active=True,
        must_change_password=True,
        is_test_account=False,
    )
    db.add(account)
    db.flush()
    db.add(StudentAccount(user_id=account.id, student_id=student.id))
    return student


def manifest_reference(revision_id: str, source_row: int) -> str:
    return f"{revision_id}:Admission!{source_row}"


def import_revision(
    db: Session,
    manifest: dict,
    actor: User,
    *,
    apply: bool,
) -> dict:
    if actor.role != "owner" or not actor.is_active:
        raise AdmissionRevisionConflict("An active owner account is required")
    preview = _preview(db, manifest)
    if not apply or preview["alreadyApplied"]:
        return preview

    revision_id = manifest["revisionId"]
    by_name, by_legacy_id = _student_indexes(db)
    cutoff = manifest["paymentCutoff"]
    payment_line = 0
    created_students = []
    changed_students = []
    created_payments = []

    for row in manifest["records"]:
        data = row["normalized"]
        student = _match_student(row, by_name, by_legacy_id)
        if row["action"] == "create":
            student = _create_student(db, row, actor, revision_id)
            by_name[_name_key(student.full_name)] = student
            if student.legacy_import_id:
                by_legacy_id[student.legacy_import_id] = student
            created_students.append(student.full_name)
        elif not student:
            raise AdmissionRevisionConflict(f"Student not found: {data['studentName']}")

        before = {
            "status": student.status,
            "dataQualityStatus": student.data_quality_status,
        }
        if row["action"] == "status_change" and row["recordStatus"] == "cancelled":
            previous_status = student.status
            if previous_status != "forfeited":
                student.status = "forfeited"
                lifecycle = _apply_student_lifecycle(
                    db,
                    student=student,
                    actor=actor,
                    previous_status=previous_status,
                    reason="Client revised admission register: moved to Cancelled / forfeited",
                )
                changed_students.append({
                    "name": student.full_name,
                    "status": "forfeited",
                    "feeClosure": lifecycle["adjustmentAmount"],
                })
        elif row["recordStatus"] == "active":
            agreement = _agreement(db, student)
            expected_delta = int(data["registrationTotal"]) - int(data["baselinePaid"] or 0)
            latest_total = sum(
                int(payment["amount"] or 0)
                for payment in _new_payments(row, cutoff)
            )
            if student.full_name != "Kautuk Sakhare":
                enrollment = (
                    db.query(Enrollment)
                    .filter_by(student_id=student.id, is_active=True)
                    .order_by(Enrollment.created_at.desc())
                    .first()
                )
                if enrollment:
                    enrollment.program = canonical_program(data["program"])
                profile = db.get(StudentAcademicProfile, student.id)
                if profile:
                    profile.source_stream = canonical_program(data["program"])
            if row["action"] == "create" or expected_delta == latest_total:
                agreement.legacy_registration_total = int(data["registrationTotal"])
            if row["action"] != "create":
                current_paid = _current_paid(db, agreement)
                baseline_paid = int(data["baselinePaid"] or 0)
                revised_paid = int(data["registrationTotal"])
                if current_paid not in {baseline_paid, revised_paid}:
                    raise AdmissionRevisionConflict(
                        f"Current ledger total for {student.full_name} no longer reconciles"
                    )
                payments_to_create = (
                    _new_payments(row, cutoff)
                    if current_paid == baseline_paid
                    and revised_paid > baseline_paid
                    else []
                )
                for payment in payments_to_create:
                    payment_line += 1
                    db.add(PaymentTransaction(
                        student_id=student.id,
                        fee_agreement_id=agreement.id,
                        legacy_import_id=revision_id,
                        legacy_line_number=payment_line,
                        transaction_date=_date(payment["transactionDate"]),
                        amount=int(payment["amount"]),
                        method=payment["method"],
                        transaction_type="payment",
                        source_note=payment["sourceNote"],
                        reference=manifest_reference(revision_id, row["sourceRow"]),
                        notes="Client-confirmed admission register revision.",
                        created_by=actor.id,
                        status="posted",
                        reconciliation_status="ready",
                    ))
                    created_payments.append({
                        "name": student.full_name,
                        "amount": int(payment["amount"]),
                        "date": payment["transactionDate"],
                    })
        if (
            student.status == "active"
            and (
                row.get("issues")
                or (
                    row["recordStatus"] == "active"
                    and int(data["registrationTotal"]) - int(data["baselinePaid"] or 0)
                    != sum(int(payment["amount"] or 0) for payment in _new_payments(row, cutoff))
                )
            )
        ):
            student.data_quality_status = "review"
        after = {
            "status": student.status,
            "dataQualityStatus": student.data_quality_status,
            "source": row["raw"],
            "issues": row.get("issues", []),
        }
        db.add(AuditLog(
            actor_id=actor.id,
            action="admission.revision.row",
            entity_type="student",
            entity_id=student.id,
            before=jsonable_encoder(before),
            after=jsonable_encoder(after),
            request_id=revision_id,
        ))

    result = {
        **preview,
        "applied": True,
        "newStudents": created_students,
        "statusChanges": changed_students,
        "payments": created_payments,
    }
    db.add(AuditLog(
        actor_id=actor.id,
        action="admission.revision.import",
        entity_type="admission_revision",
        entity_id=revision_id,
        before=None,
        after=jsonable_encoder(result),
        request_id=revision_id,
    ))
    db.commit()
    return result
