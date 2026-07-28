from app.models import AuditLog, Student, StudentAccount, User
from app.security import verify_password
from scripts.provision_student_accounts import (
    provision_student_accounts,
    verify_credentials,
    write_credentials,
)


def test_bulk_student_provisioning_is_scoped_audited_and_idempotent(database, tmp_path):
    owner = database.query(User).filter_by(role="owner").one()
    eligible = Student(
        admission_number="LI-2026-00901",
        full_name="Eligible Student",
        mobile="+91 98765 43210",
        status="active",
    )
    missing = Student(
        admission_number="LI-2026-00902",
        full_name="Missing Number",
        status="active",
    )
    forfeited = Student(
        admission_number="LI-2026-00903",
        full_name="Forfeited Student",
        mobile="9876543211",
        status="forfeited",
    )
    conflict = Student(
        admission_number="LI-2026-00904",
        full_name="Existing User Conflict",
        mobile=owner.mobile,
        status="active",
    )
    database.add_all([eligible, missing, forfeited, conflict])
    database.commit()

    preview = provision_student_accounts(database, owner, apply=False)
    assert preview["activeStudents"] == 3
    assert preview["eligibleAccounts"] == 1
    assert [item["fullName"] for item in preview["missingMobile"]] == ["Missing Number"]
    assert [item["fullName"] for item in preview["conflicts"]] == ["Existing User Conflict"]
    assert preview["createdAccounts"] == 0
    database.rollback()

    created = provision_student_accounts(
        database,
        owner,
        apply=True,
        password_factory=lambda: "UniquePass123!",
    )
    database.commit()
    assert created["createdAccounts"] == 1
    account = (
        database.query(StudentAccount)
        .filter_by(student_id=eligible.id)
        .one()
    )
    user = database.get(User, account.user_id)
    assert user.mobile == "9876543210"
    assert user.role == "student"
    assert user.must_change_password is True
    assert verify_password("UniquePass123!", user.password_hash)
    assert database.query(StudentAccount).filter_by(student_id=forfeited.id).count() == 0
    assert database.query(AuditLog).filter_by(
        action="settings.student_access.bulk_create",
        entity_id=eligible.id,
    ).count() == 1
    credentials_path = tmp_path / "student-credentials.csv"
    write_credentials(credentials_path, created["credentials"])
    verified = verify_credentials(database, credentials_path)
    assert verified == {"credentials": 1, "liveLogins": 0}
    assert credentials_path.stat().st_mode & 0o777 == 0o600

    rerun = provision_student_accounts(database, owner, apply=True)
    database.commit()
    assert rerun["createdAccounts"] == 0
    assert rerun["existingAccounts"] == 1


def test_bulk_student_provisioning_rejects_non_owner(database):
    parent = database.query(User).filter_by(role="parent_student").one()
    try:
        provision_student_accounts(database, parent, apply=False)
    except RuntimeError as error:
        assert str(error) == "An active owner account is required"
    else:
        raise AssertionError("Expected a non-owner provisioning request to be rejected")
