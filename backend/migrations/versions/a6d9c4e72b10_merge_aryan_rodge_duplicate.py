"""Merge the duplicate Essential record for Aryan Rodge.

The complete ERP profile (LI-2026-00071) is retained.  The academic source
identity E-42 and all finance, attendance, portal and activity links from
LI-2026-00072 are moved to that profile before the duplicate is removed.
"""

from datetime import datetime, timezone

from alembic import op
import sqlalchemy as sa


revision = "a6d9c4e72b10"
down_revision = "f4b8c1d2e903"
branch_labels = None
depends_on = None

KEEP_STUDENT_ID = "stu_97ee600603834fe59600a3a3d236d487"
DUPLICATE_STUDENT_ID = "stu_74681cd0e6bb45e5b24b03a0da39273e"


def _row(bind, statement: str, **params):
    return bind.execute(sa.text(statement), params).mappings().first()


def _delete_conflicting_pairs(bind, table: str, key_columns: tuple[str, ...]):
    comparisons = " AND ".join(f"kept.{column} = duplicate.{column}" for column in key_columns)
    bind.execute(sa.text(f"""
        DELETE FROM {table}
        WHERE student_id = :duplicate_id
          AND EXISTS (
              SELECT 1
              FROM {table} AS kept
              WHERE kept.student_id = :keep_id
                AND {comparisons.replace('duplicate.', f'{table}.')}
          )
    """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})
    bind.execute(sa.text(f"""
        UPDATE {table}
        SET student_id = :keep_id
        WHERE student_id = :duplicate_id
    """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})


def _merge_portal_links(bind):
    kept_account = _row(
        bind,
        "SELECT user_id FROM student_accounts WHERE student_id = :student_id",
        student_id=KEEP_STUDENT_ID,
    )
    duplicate_account = _row(
        bind,
        "SELECT user_id FROM student_accounts WHERE student_id = :student_id",
        student_id=DUPLICATE_STUDENT_ID,
    )
    if duplicate_account and kept_account:
        bind.execute(
            sa.text("DELETE FROM student_accounts WHERE student_id = :student_id"),
            {"student_id": DUPLICATE_STUDENT_ID},
        )
    elif duplicate_account:
        bind.execute(sa.text("""
            UPDATE student_accounts SET student_id = :keep_id WHERE student_id = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})

    bind.execute(sa.text("""
        UPDATE users
        SET full_name = 'Aryan Gopal Rodge'
        WHERE id IN (SELECT user_id FROM student_accounts WHERE student_id = :keep_id)
    """), {"keep_id": KEEP_STUDENT_ID})

    bind.execute(sa.text("""
        UPDATE parent_accounts SET student_id = :keep_id WHERE student_id = :duplicate_id
    """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})
    _delete_conflicting_pairs(bind, "student_guardians", ("guardian_id",))


def _merge_academics(bind):
    kept = _row(
        bind,
        "SELECT * FROM student_academic_profiles WHERE student_id = :student_id",
        student_id=KEEP_STUDENT_ID,
    )
    duplicate = _row(
        bind,
        "SELECT * FROM student_academic_profiles WHERE student_id = :student_id",
        student_id=DUPLICATE_STUDENT_ID,
    )
    if duplicate and kept:
        bind.execute(
            sa.text("DELETE FROM student_academic_profiles WHERE student_id = :student_id"),
            {"student_id": DUPLICATE_STUDENT_ID},
        )
        bind.execute(sa.text("""
            UPDATE student_academic_profiles
            SET source_student_code = :source_student_code,
                batch_name = COALESCE(NULLIF(batch_name, ''), :batch_name),
                source_stream = COALESCE(NULLIF(source_stream, ''), :source_stream),
                mentor_name = COALESCE(NULLIF(mentor_name, ''), :mentor_name),
                source_school_name = COALESCE(NULLIF(source_school_name, ''), :source_school_name),
                source_primary_mobile = COALESCE(NULLIF(source_primary_mobile, ''), :source_primary_mobile),
                source_secondary_mobile = COALESCE(NULLIF(source_secondary_mobile, ''), :source_secondary_mobile),
                import_batch_id = :import_batch_id
            WHERE student_id = :keep_id
        """), {
            "keep_id": KEEP_STUDENT_ID,
            "source_student_code": duplicate["source_student_code"],
            "batch_name": duplicate["batch_name"],
            "source_stream": duplicate["source_stream"],
            "mentor_name": duplicate["mentor_name"],
            "source_school_name": duplicate["source_school_name"],
            "source_primary_mobile": duplicate["source_primary_mobile"],
            "source_secondary_mobile": duplicate["source_secondary_mobile"],
            "import_batch_id": duplicate["import_batch_id"],
        })
    elif duplicate:
        bind.execute(sa.text("""
            UPDATE student_academic_profiles SET student_id = :keep_id WHERE student_id = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})

    _delete_conflicting_pairs(bind, "student_subject_selections", ("subject_name",))
    _delete_conflicting_pairs(bind, "daily_attendance_entries", ("source_sheet", "source_date_label"))
    _delete_conflicting_pairs(bind, "attendance_period_summaries", ("period_start", "period_end"))

    for table in ("academic_source_records", "device_attendance_identities", "biometric_attendance_days"):
        bind.execute(sa.text(f"""
            UPDATE {table} SET student_id = :keep_id WHERE student_id = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})
    bind.execute(sa.text("""
        UPDATE device_attendance_identities
        SET device_name = 'Aryan Gopal Rodge'
        WHERE student_id = :keep_id
    """), {"keep_id": KEEP_STUDENT_ID})


def _merge_fee_agreements(bind, keep_enrollment_id: str | None, duplicate_enrollment_id: str | None):
    kept_fee = _row(
        bind,
        "SELECT * FROM fee_agreements WHERE student_id = :student_id ORDER BY created_at DESC LIMIT 1",
        student_id=KEEP_STUDENT_ID,
    )
    duplicate_fee = _row(
        bind,
        "SELECT * FROM fee_agreements WHERE student_id = :student_id ORDER BY created_at DESC LIMIT 1",
        student_id=DUPLICATE_STUDENT_ID,
    )
    if duplicate_fee and kept_fee:
        bind.execute(sa.text("""
            UPDATE payment_transactions
            SET student_id = :keep_id, fee_agreement_id = :kept_fee_id
            WHERE student_id = :duplicate_id OR fee_agreement_id = :duplicate_fee_id
        """), {
            "keep_id": KEEP_STUDENT_ID,
            "duplicate_id": DUPLICATE_STUDENT_ID,
            "kept_fee_id": kept_fee["id"],
            "duplicate_fee_id": duplicate_fee["id"],
        })
        bind.execute(sa.text("""
            UPDATE fee_installments
            SET student_id = :keep_id, fee_agreement_id = :kept_fee_id
            WHERE student_id = :duplicate_id OR fee_agreement_id = :duplicate_fee_id
        """), {
            "keep_id": KEEP_STUDENT_ID,
            "duplicate_id": DUPLICATE_STUDENT_ID,
            "kept_fee_id": kept_fee["id"],
            "duplicate_fee_id": duplicate_fee["id"],
        })
        duplicate_legacy_id = duplicate_fee["legacy_import_id"]
        bind.execute(sa.text("""
            UPDATE fee_agreements SET legacy_import_id = NULL WHERE id = :duplicate_fee_id
        """), {"duplicate_fee_id": duplicate_fee["id"]})
        bind.execute(sa.text("""
            UPDATE fee_agreements
            SET agreed_amount = CASE WHEN agreed_amount > :agreed_amount THEN agreed_amount ELSE :agreed_amount END,
                legacy_registration_total = CASE
                    WHEN legacy_registration_total > :registration_total THEN legacy_registration_total
                    ELSE :registration_total
                END,
                legacy_import_id = COALESCE(legacy_import_id, :legacy_import_id)
            WHERE id = :kept_fee_id
        """), {
            "kept_fee_id": kept_fee["id"],
            "agreed_amount": duplicate_fee["agreed_amount"],
            "registration_total": duplicate_fee["legacy_registration_total"],
            "legacy_import_id": duplicate_legacy_id,
        })
        bind.execute(
            sa.text("DELETE FROM fee_agreements WHERE id = :duplicate_fee_id"),
            {"duplicate_fee_id": duplicate_fee["id"]},
        )
    elif duplicate_fee:
        bind.execute(sa.text("""
            UPDATE fee_agreements
            SET student_id = :keep_id, enrollment_id = :keep_enrollment_id
            WHERE id = :duplicate_fee_id
        """), {
            "keep_id": KEEP_STUDENT_ID,
            "keep_enrollment_id": keep_enrollment_id or duplicate_enrollment_id,
            "duplicate_fee_id": duplicate_fee["id"],
        })
        bind.execute(sa.text("""
            UPDATE payment_transactions SET student_id = :keep_id WHERE student_id = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})
        bind.execute(sa.text("""
            UPDATE fee_installments SET student_id = :keep_id WHERE student_id = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})


def _merge_enrollment_and_finance(bind):
    kept_enrollment = _row(bind, """
        SELECT * FROM enrollments
        WHERE student_id = :student_id
        ORDER BY is_active DESC, created_at DESC, id DESC LIMIT 1
    """, student_id=KEEP_STUDENT_ID)
    duplicate_enrollment = _row(bind, """
        SELECT * FROM enrollments
        WHERE student_id = :student_id
        ORDER BY is_active DESC, created_at DESC, id DESC LIMIT 1
    """, student_id=DUPLICATE_STUDENT_ID)
    kept_enrollment_id = kept_enrollment["id"] if kept_enrollment else None
    duplicate_enrollment_id = duplicate_enrollment["id"] if duplicate_enrollment else None

    if kept_enrollment and duplicate_enrollment and not kept_enrollment["legacy_import_id"]:
        duplicate_legacy_id = duplicate_enrollment["legacy_import_id"]
        bind.execute(sa.text("""
            UPDATE enrollments SET legacy_import_id = NULL WHERE id = :duplicate_enrollment_id
        """), {"duplicate_enrollment_id": duplicate_enrollment_id})
        bind.execute(sa.text("""
            UPDATE enrollments SET legacy_import_id = :legacy_import_id WHERE id = :kept_enrollment_id
        """), {"legacy_import_id": duplicate_legacy_id, "kept_enrollment_id": kept_enrollment_id})
    elif duplicate_enrollment and not kept_enrollment:
        bind.execute(sa.text("""
            UPDATE enrollments SET student_id = :keep_id WHERE id = :duplicate_enrollment_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_enrollment_id": duplicate_enrollment_id})
        kept_enrollment_id = duplicate_enrollment_id

    _merge_fee_agreements(bind, kept_enrollment_id, duplicate_enrollment_id)

    kept_handoff = _row(
        bind,
        "SELECT id FROM finance_handoffs WHERE student_id = :student_id",
        student_id=KEEP_STUDENT_ID,
    )
    duplicate_handoff = _row(
        bind,
        "SELECT id FROM finance_handoffs WHERE student_id = :student_id",
        student_id=DUPLICATE_STUDENT_ID,
    )
    if duplicate_handoff and kept_handoff:
        bind.execute(
            sa.text("DELETE FROM finance_handoffs WHERE id = :handoff_id"),
            {"handoff_id": duplicate_handoff["id"]},
        )
    elif duplicate_handoff:
        bind.execute(sa.text("""
            UPDATE finance_handoffs
            SET student_id = :keep_id, enrollment_id = :keep_enrollment_id
            WHERE id = :handoff_id
        """), {
            "keep_id": KEEP_STUDENT_ID,
            "keep_enrollment_id": kept_enrollment_id,
            "handoff_id": duplicate_handoff["id"],
        })

    if kept_enrollment and duplicate_enrollment:
        bind.execute(
            sa.text("DELETE FROM enrollments WHERE student_id = :student_id"),
            {"student_id": DUPLICATE_STUDENT_ID},
        )


def _merge_remaining_links(bind):
    for table, keys in (
        ("attendance_entries", ("register_id",)),
        ("assignment_recipients", ("assignment_id",)),
        ("assignment_downloads", ("assignment_id",)),
        ("examination_participants", ("exam_id",)),
        ("examination_results", ("exam_id",)),
    ):
        _delete_conflicting_pairs(bind, table, keys)

    bind.execute(sa.text("""
        UPDATE examination_participants
        SET admission_number = 'LI-2026-00071', full_name = 'Aryan Gopal Rodge'
        WHERE student_id = :keep_id
    """), {"keep_id": KEEP_STUDENT_ID})

    for table, column in (
        ("communication_threads", "student_id"),
        ("inventory_movements", "student_id"),
        ("leads", "converted_student_id"),
    ):
        bind.execute(sa.text(f"""
            UPDATE {table} SET {column} = :keep_id WHERE {column} = :duplicate_id
        """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})

    kept_legacy = _row(
        bind,
        "SELECT id FROM legacy_admission_rows WHERE student_id = :student_id",
        student_id=KEEP_STUDENT_ID,
    )
    if kept_legacy:
        bind.execute(sa.text("""
            UPDATE legacy_admission_rows SET student_id = NULL WHERE student_id = :keep_id
        """), {"keep_id": KEEP_STUDENT_ID})
    bind.execute(sa.text("""
        UPDATE legacy_admission_rows SET student_id = :keep_id WHERE student_id = :duplicate_id
    """), {"keep_id": KEEP_STUDENT_ID, "duplicate_id": DUPLICATE_STUDENT_ID})


def upgrade():
    bind = op.get_bind()
    kept = _row(bind, "SELECT * FROM students WHERE id = :student_id", student_id=KEEP_STUDENT_ID)
    duplicate = _row(bind, "SELECT * FROM students WHERE id = :student_id", student_id=DUPLICATE_STUDENT_ID)
    if not kept or not duplicate:
        return

    _merge_portal_links(bind)
    _merge_academics(bind)
    _merge_enrollment_and_finance(bind)
    _merge_remaining_links(bind)

    bind.execute(sa.text("""
        UPDATE students
        SET full_name = 'Aryan Gopal Rodge',
            mobile = COALESCE(NULLIF(mobile, ''), :mobile),
            secondary_mobile = COALESCE(NULLIF(secondary_mobile, ''), :secondary_mobile),
            email = COALESCE(NULLIF(email, ''), :email),
            previous_school = COALESCE(NULLIF(previous_school, ''), :previous_school),
            status = CASE WHEN status = 'active' OR :duplicate_status = 'active' THEN 'active' ELSE status END
        WHERE id = :keep_id
    """), {
        "keep_id": KEEP_STUDENT_ID,
        "mobile": duplicate["mobile"],
        "secondary_mobile": duplicate["secondary_mobile"],
        "email": duplicate["email"],
        "previous_school": duplicate["previous_school"],
        "duplicate_status": duplicate["status"],
    })
    bind.execute(
        sa.text("DELETE FROM students WHERE id = :duplicate_id"),
        {"duplicate_id": DUPLICATE_STUDENT_ID},
    )
    audit_insert = sa.text("""
        INSERT INTO audit_logs
            (id, actor_id, action, entity_type, entity_id, before, after, request_id, created_at)
        VALUES
            (:id, NULL, 'student.duplicate_merged', 'student', :entity_id,
             :before, :after, NULL, :created_at)
    """).bindparams(
        sa.bindparam("before", type_=sa.JSON()),
        sa.bindparam("after", type_=sa.JSON()),
    )
    bind.execute(audit_insert, {
        "id": "aud_merge_aryan_rodge_20260905",
        "entity_id": KEEP_STUDENT_ID,
        "before": {
            "keptStudentId": KEEP_STUDENT_ID,
            "duplicateStudentId": DUPLICATE_STUDENT_ID,
            "duplicateAdmissionNumber": duplicate["admission_number"],
            "duplicateName": duplicate["full_name"],
        },
        "after": {
            "studentId": KEEP_STUDENT_ID,
            "admissionNumber": "LI-2026-00071",
            "fullName": "Aryan Gopal Rodge",
            "academicSourceId": "E-42",
            "duplicateRemoved": True,
        },
        "created_at": datetime.now(timezone.utc),
    })


def downgrade():
    # The duplicate cannot be reconstructed safely after its finance and
    # attendance histories have been consolidated into the retained profile.
    pass
