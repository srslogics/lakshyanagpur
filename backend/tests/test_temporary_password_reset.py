from app.models import AuditLog, Student, StudentAccount, User
from app.security import hash_password, verify_password
from scripts.provision_faculty_accounts import FACULTY_EMAILS
from scripts.reset_portal_temporary_passwords import reset_portal_passwords


def test_shared_temporary_password_targets_only_active_student_and_real_faculty(
    database,
):
    owner = database.query(User).filter_by(role="owner").one()
    student = Student(
        admission_number="LI-2026-09991",
        full_name="Portal Student",
        mobile="9876500991",
        status="active",
    )
    inactive_student = Student(
        admission_number="LI-2026-09992",
        full_name="Inactive Student",
        mobile="9876500992",
        status="forfeited",
    )
    student_user = User(
        mobile=student.mobile,
        full_name=student.full_name,
        role="student",
        password_hash=hash_password("OldPassword123!"),
    )
    inactive_user = User(
        mobile=inactive_student.mobile,
        full_name=inactive_student.full_name,
        role="student",
        password_hash=hash_password("OldPassword123!"),
    )
    faculty = User(
        email=FACULTY_EMAILS["Meet Sir"],
        full_name="Meet Sir",
        role="faculty",
        password_hash=hash_password("OldPassword123!"),
    )
    demo_faculty = User(
        email="faculty.demo@example.com",
        full_name="Lakshya Faculty Demo",
        role="faculty",
        password_hash=hash_password("OldPassword123!"),
    )
    database.add_all([
        student,
        inactive_student,
        student_user,
        inactive_user,
        faculty,
        demo_faculty,
    ])
    database.flush()
    database.add_all([
        StudentAccount(user_id=student_user.id, student_id=student.id),
        StudentAccount(user_id=inactive_user.id, student_id=inactive_student.id),
    ])
    database.commit()

    result = reset_portal_passwords(
        database,
        owner,
        "Lakshya@2026!",
        apply=True,
    )
    database.commit()
    assert result["studentAccounts"] == 1
    assert result["facultyAccounts"] == 1
    assert result["resetAccounts"] == 2
    assert student_user.must_change_password is True
    assert faculty.must_change_password is True
    assert verify_password("Lakshya@2026!", student_user.password_hash)
    assert verify_password("Lakshya@2026!", faculty.password_hash)
    assert inactive_user.must_change_password is False
    assert demo_faculty.must_change_password is False
    assert database.query(AuditLog).filter_by(
        action="auth.temporary_password.reset",
    ).count() == 2

    rerun = reset_portal_passwords(
        database,
        owner,
        "Lakshya@2026!",
        apply=True,
    )
    database.commit()
    assert rerun["resetAccounts"] == 0
