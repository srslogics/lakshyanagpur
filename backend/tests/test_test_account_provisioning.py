from app.models import ParentAccount, Student, StudentAccount, User
from app.security import verify_password
from scripts.provision_test_accounts import (
    ACCOUNT_SPECS,
    DEMO_ADMISSION_NUMBER,
    provision_test_accounts,
)


PASSWORDS = {
    "student": "StudentTestPass123!",
    "parent": "ParentTestPass123!",
    "faculty": "FacultyTestPass123!",
    "attendance": "AttendanceTestPass123!",
}


def test_test_accounts_are_isolated_and_idempotent(database):
    first = provision_test_accounts(database, PASSWORDS)
    second = provision_test_accounts(database, PASSWORDS)

    assert first["admissionNumber"] == DEMO_ADMISSION_NUMBER
    assert second["studentId"] == first["studentId"]
    assert database.query(User).filter(
        User.mobile.in_([spec["mobile"] for spec in ACCOUNT_SPECS.values()])
    ).count() == 4

    student = database.query(Student).filter_by(
        admission_number=DEMO_ADMISSION_NUMBER
    ).one()
    assert student.status == "inactive"
    assert database.query(StudentAccount).filter_by(student_id=student.id).count() == 1
    assert database.query(ParentAccount).filter_by(student_id=student.id).count() == 1

    for key, spec in ACCOUNT_SPECS.items():
        user = database.query(User).filter_by(mobile=spec["mobile"]).one()
        assert user.role == spec["role"]
        assert verify_password(PASSWORDS[key], user.password_hash)
