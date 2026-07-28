from app.models import AuditLog, User
from scripts.provision_faculty_accounts import (
    FACULTY_EMAILS,
    provision_faculty_accounts,
    verify_credentials,
    write_credentials,
)


def test_faculty_email_provisioning_is_audited_and_idempotent(database, tmp_path):
    owner = database.query(User).filter_by(role="owner").one()
    faculty = [
        User(
            full_name=full_name,
            role="faculty",
            password_hash="unprovisioned",
        )
        for full_name in FACULTY_EMAILS
    ]
    database.add_all(faculty)
    database.commit()

    preview = provision_faculty_accounts(database, owner, apply=False)
    assert preview["eligibleAccounts"] == 5
    assert preview["createdAccounts"] == 0
    database.rollback()

    created = provision_faculty_accounts(
        database,
        owner,
        apply=True,
        password_factory=lambda: "FacultyFirst123!",
    )
    database.commit()
    assert created["createdAccounts"] == 5
    assert database.query(AuditLog).filter_by(
        action="settings.faculty_access.email_onboard",
    ).count() == 5
    credentials_path = tmp_path / "faculty-credentials.csv"
    write_credentials(credentials_path, created["credentials"])
    assert verify_credentials(database, credentials_path) == 5
    assert credentials_path.stat().st_mode & 0o777 == 0o600

    rerun = provision_faculty_accounts(database, owner, apply=True)
    database.commit()
    assert rerun["createdAccounts"] == 0
    assert rerun["existingAccounts"] == 5


def test_faculty_email_provisioning_reports_missing_profiles(database):
    owner = database.query(User).filter_by(role="owner").one()
    preview = provision_faculty_accounts(database, owner, apply=False)
    assert preview["eligibleAccounts"] == 0
    assert len(preview["missingProfiles"]) == 5
