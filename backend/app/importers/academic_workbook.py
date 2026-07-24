from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

from sqlalchemy.orm import Session

from ..database import SessionLocal
from ..models import (
    AcademicImportBatch,
    AcademicSourceRecord,
    AuditLog,
    Batch,
    DailyAttendanceEntry,
    Enrollment,
    Student,
    StudentAcademicProfile,
    StudentSubjectSelection,
)


class AcademicImportConflict(ValueError):
    pass


def _canonical_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "", value.casefold())


def _date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None


def _calculated(manifest: dict) -> dict:
    records = manifest.get("students", [])
    source_records = manifest.get("source_records", [])
    attendance = [entry for record in records for entry in record.get("attendance", [])]
    subjects = [subject for record in records for subject in record.get("subjects", [])]
    raw_counts: dict[str, int] = {}
    for entry in attendance:
        raw = entry["raw_status"]
        raw_counts[raw] = raw_counts.get(raw, 0) + 1
    batch_counts: dict[str, int] = {}
    for record in records:
        batch = record["batch"]
        batch_counts[batch] = batch_counts.get(batch, 0) + 1
    return {
        "active_students": len(records),
        "batch_counts": batch_counts,
        "mentor_assignments": sum(bool(record.get("mentor_name")) for record in records),
        "subject_selections": len(subjects),
        "attendance_entries": len(attendance),
        "attendance_marks": raw_counts,
        "source_records": len(source_records),
        "unresolved_items": sum(len(record.get("issues", [])) for record in records)
        + sum(len(record.get("issues", [])) for record in source_records),
    }


def _validate(manifest: dict) -> None:
    if manifest.get("schema_version") != 1:
        raise AcademicImportConflict("Unsupported academic workbook manifest schema")
    calculated = _calculated(manifest)
    if calculated != manifest.get("expected"):
        raise AcademicImportConflict(
            f"Manifest reconciliation failed: expected {manifest.get('expected')}, calculated {calculated}"
        )
    codes = [record["source_student_code"] for record in manifest["students"]]
    if len(codes) != len(set(codes)):
        raise AcademicImportConflict("Manifest contains duplicate source student codes")
    source_ids = [record["id"] for record in manifest["source_records"]]
    if len(source_ids) != len(set(source_ids)):
        raise AcademicImportConflict("Manifest contains duplicate source record IDs")
    valid_marks = {"P", "A", "X"}
    for record in manifest["students"]:
        for entry in record.get("attendance", []):
            if entry["raw_status"] not in valid_marks:
                raise AcademicImportConflict(
                    f"Unsupported attendance mark {entry['raw_status']!r} for {record['source_student_code']}"
                )
            expected_status = {"P": "present", "A": "absent", "X": None}[entry["raw_status"]]
            if entry.get("normalized_status") != expected_status:
                raise AcademicImportConflict(
                    f"Attendance normalization changed source meaning for {record['source_student_code']}"
                )


def _student_for_record(db: Session, record: dict) -> Student:
    student = (
        db.query(Student)
        .filter_by(legacy_import_id=record["admission_legacy_id"])
        .one_or_none()
    )
    if not student:
        raise AcademicImportConflict(
            f"Admission student {record['admission_legacy_id']} is missing; import admissions first"
        )
    if _canonical_name(student.full_name) != _canonical_name(record["student_name"]):
        raise AcademicImportConflict(
            f"Student identity mismatch for {record['source_student_code']}: "
            f"{student.full_name!r} vs {record['student_name']!r}"
        )
    return student


def _upsert_profile(db: Session, batch: AcademicImportBatch, student: Student, record: dict) -> None:
    existing_code = (
        db.query(StudentAcademicProfile)
        .filter_by(source_student_code=record["source_student_code"])
        .one_or_none()
    )
    if existing_code and existing_code.student_id != student.id:
        raise AcademicImportConflict(
            f"Source code {record['source_student_code']} is already linked to another student"
        )
    profile = db.get(StudentAcademicProfile, student.id)
    if not profile:
        profile = StudentAcademicProfile(
            student_id=student.id,
            source_student_code=record["source_student_code"],
            batch_name=record["batch"],
            import_batch_id=batch.id,
        )
        db.add(profile)
    profile.source_student_code = record["source_student_code"]
    profile.batch_name = record["batch"]
    profile.source_stream = record.get("source_stream")
    profile.mentor_name = record.get("mentor_name")
    profile.source_school_name = record.get("source_school_name")
    profile.source_primary_mobile = record.get("source_primary_mobile")
    profile.source_secondary_mobile = record.get("source_secondary_mobile")
    profile.import_batch_id = batch.id

    enrollment = (
        db.query(Enrollment)
        .filter_by(student_id=student.id, is_active=True)
        .order_by(Enrollment.created_at.desc())
        .first()
    )
    if not enrollment:
        raise AcademicImportConflict(
            f"Active enrollment is missing for {record['source_student_code']}"
        )
    enrollment.batch = record["batch"]
    db.flush()
    if not db.query(Batch).filter_by(name=record["batch"], program=enrollment.program).first():
        db.add(Batch(name=record["batch"], program=enrollment.program, is_active=True))

    db.query(StudentSubjectSelection).filter_by(student_id=student.id).delete(
        synchronize_session=False
    )
    for subject in record.get("subjects", []):
        db.add(
            StudentSubjectSelection(
                student_id=student.id,
                subject_name=subject["name"],
                source_value=subject["source_value"],
                import_batch_id=batch.id,
            )
        )

    for entry in record.get("attendance", []):
        attendance = (
            db.query(DailyAttendanceEntry)
            .filter_by(
                student_id=student.id,
                source_sheet=record["source_sheet"],
                source_date_label=entry["source_date_label"],
            )
            .one_or_none()
        )
        if not attendance:
            attendance = DailyAttendanceEntry(
                student_id=student.id,
                import_batch_id=batch.id,
                source_student_code=record["source_student_code"],
                batch_name=record["batch"],
                source_sheet=record["source_sheet"],
                source_row=record["source_row"],
                source_column=entry["source_column"],
                source_date_label=entry["source_date_label"],
                attendance_date=_date(entry.get("attendance_date")),
                raw_status=entry["raw_status"],
                normalized_status=entry.get("normalized_status"),
            )
            db.add(attendance)
        else:
            attendance.import_batch_id = batch.id
            attendance.source_student_code = record["source_student_code"]
            attendance.batch_name = record["batch"]
            attendance.source_row = record["source_row"]
            attendance.source_column = entry["source_column"]
            attendance.attendance_date = _date(entry.get("attendance_date"))
            attendance.raw_status = entry["raw_status"]
            attendance.normalized_status = entry.get("normalized_status")


def import_manifest(db: Session, manifest: dict, actor_id: str | None = None) -> dict:
    _validate(manifest)
    source = manifest["source"]
    previous = (
        db.query(AcademicImportBatch)
        .filter_by(source_hash=source["sha256"])
        .one_or_none()
    )
    if previous:
        return reconciliation(db, previous.id, idempotent=True)

    expected = manifest["expected"]
    batch = AcademicImportBatch(
        source_name=source["name"],
        source_hash=source["sha256"],
        status="completed_with_review" if expected["unresolved_items"] else "completed",
        active_student_rows=expected["active_students"],
        attendance_entries=expected["attendance_entries"],
        subject_selections=expected["subject_selections"],
        staged_source_rows=expected["source_records"],
        unresolved_items=expected["unresolved_items"],
        actor_id=actor_id,
    )
    db.add(batch)
    db.flush()

    try:
        students: dict[str, Student] = {}
        for record in manifest["students"]:
            student = _student_for_record(db, record)
            students[record["source_student_code"]] = student
            _upsert_profile(db, batch, student, record)

        for row in manifest["source_records"]:
            existing = db.get(AcademicSourceRecord, row["id"])
            if existing:
                if existing.raw_data != row["raw"] or existing.normalized_data != row["normalized"]:
                    raise AcademicImportConflict(
                        f"Source record {row['id']} already exists with different data"
                    )
                continue
            source_key = row.get("source_key")
            linked = students.get(source_key) if source_key else None
            db.add(
                AcademicSourceRecord(
                    id=row["id"],
                    import_batch_id=batch.id,
                    source_sheet=row["source_sheet"],
                    source_row=row["source_row"],
                    record_type=row["record_type"],
                    source_key=source_key,
                    raw_data=row["raw"],
                    normalized_data=row["normalized"],
                    issues=row.get("issues", []),
                    student_id=linked.id if linked else None,
                )
            )

        db.add(
            AuditLog(
                actor_id=actor_id,
                action="migration.academics.import",
                entity_type="academic_import_batch",
                entity_id=batch.id,
                before=None,
                after=expected,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
        raise
    return reconciliation(db, batch.id)


def reconciliation(db: Session, batch_id: str, idempotent: bool = False) -> dict:
    batch = db.get(AcademicImportBatch, batch_id)
    if not batch:
        raise AcademicImportConflict("Academic import batch not found")
    profiles = db.query(StudentAcademicProfile).filter_by(import_batch_id=batch.id).count()
    attendance = db.query(DailyAttendanceEntry).filter_by(import_batch_id=batch.id)
    marks = {
        mark: attendance.filter_by(raw_status=mark).count()
        for mark in ("P", "A", "X")
    }
    return {
        "batch_id": batch.id,
        "idempotent_rerun": idempotent,
        "active_students": profiles,
        "batch_counts": {
            name: db.query(StudentAcademicProfile)
            .filter_by(import_batch_id=batch.id, batch_name=name)
            .count()
            for name in ("Tatva", "Essential")
        },
        "mentor_assignments": db.query(StudentAcademicProfile)
        .filter(
            StudentAcademicProfile.import_batch_id == batch.id,
            StudentAcademicProfile.mentor_name.is_not(None),
        )
        .count(),
        "subject_selections": db.query(StudentSubjectSelection)
        .filter_by(import_batch_id=batch.id)
        .count(),
        "attendance_entries": attendance.count(),
        "attendance_marks": marks,
        "source_records": db.query(AcademicSourceRecord)
        .filter_by(import_batch_id=batch.id)
        .count(),
        "unresolved_items": batch.unresolved_items,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Import the reviewed Lakshya academic and attendance manifest"
    )
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
