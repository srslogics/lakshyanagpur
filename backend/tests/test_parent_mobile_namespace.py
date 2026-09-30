import pytest
from sqlalchemy.exc import IntegrityError
from app.models import Student, User
from app.security import hash_password


def test_same_mobile_has_independent_parent_and_student_passwords(client, database, owner_headers):
    student = Student(full_name="Child", admission_number="SHARED-1", status="active")
    account = User(full_name="Child", role="student", mobile="9888888888", password_hash=hash_password("Student123"))
    database.add_all([student, account]); database.commit()
    original_hash = account.password_hash
    payload = {"studentId": student.id, "fullName": "Parent", "mobile": account.mobile, "password": "123456", "contactType": "primary_contact"}
    assert client.post("/api/settings/parent-access", headers=owner_headers, json=payload).status_code == 201
    database.refresh(account)
    assert account.password_hash == original_hash
    consent = {"mobile": account.mobile, "consentAccepted": True, "consentVersion": "student-parent-v1-2026-08-15"}
    for portal, password in [("student", "Student123"), ("parent", "123456")]:
        result = client.post("/api/auth/login", json={**consent, "portal": portal, "password": password})
        assert result.status_code == 200
        assert result.json()["user"]["role"] == portal
    for portal, password in [("parent", "Student123"), ("student", "123456")]:
        assert client.post("/api/auth/login", json={**consent, "portal": portal, "password": password}).status_code == 401
    assert client.post("/api/auth/login", json={**consent, "password": "123456"}).status_code == 401
    assert client.post("/api/settings/parent-access", headers=owner_headers, json=payload).status_code == 409
    assert client.post("/api/auth/portal-login", json={**consent, "portal": "parent", "password": "123456"}).json()["user"]["mustChangePassword"] is True


@pytest.mark.parametrize("role", ["parent", "student", "faculty"])
def test_database_still_prevents_duplicates_within_namespace(database, role):
    first_role = "parent" if role == "parent" else "student"
    database.add(User(full_name="First", role=first_role, mobile="9777777777", password_hash="test")); database.commit()
    database.add(User(full_name="Second", role=role, mobile="9777777777", password_hash="test"))
    with pytest.raises(IntegrityError):
        database.commit()
    database.rollback()
