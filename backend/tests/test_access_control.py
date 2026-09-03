from app.models import AuditLog, Batch, Subject, User, UserModulePermission
from app.permissions import MODULES, role_default_permissions
from app.security import create_token, hash_password


def permissions_payload(**overrides):
    permissions = {
        module: {"read": False, "create": False, "edit": False}
        for module in MODULES
    }
    permissions.update(overrides)
    return {"permissions": permissions}


def test_owner_can_create_operations_account_with_custom_access(client, database, owner_headers):
    custom_permissions = permissions_payload(
        students={"read": True, "create": False, "edit": True},
        reports={"read": True, "create": False, "edit": False},
    )["permissions"]
    response = client.post(
        "/api/settings/users",
        headers=owner_headers,
        json={
            "fullName": "Institute Director",
            "mobile": "9000000015",
            "email": "director@example.com",
            "password": "Lakshaya@2026",
            "role": "director",
            "permissions": custom_permissions,
        },
    )
    assert response.status_code == 201
    created = response.json()
    assert created["role"] == "director"
    assert created["hasCustomPermissions"] is True
    assert created["permissions"] == custom_permissions
    assert database.query(UserModulePermission).filter_by(user_id=created["id"]).count() == len(MODULES)

    login = client.post(
        "/api/auth/login",
        json={"mobile": "9000000015", "password": "Lakshaya@2026"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["permissions"] == custom_permissions


def test_director_recommended_access_is_read_only(client, database, owner_headers):
    response = client.post(
        "/api/settings/users",
        headers=owner_headers,
        json={
            "fullName": "Read Only Director",
            "mobile": "9000000016",
            "password": "Lakshaya@2026",
            "role": "director",
        },
    )
    assert response.status_code == 201
    assert response.json()["hasCustomPermissions"] is False
    assert response.json()["permissions"] == role_default_permissions("director")
    assert all(
        access == {"read": True, "create": False, "edit": False}
        for access in response.json()["permissions"].values()
    )
    director = database.get(User, response.json()["id"])
    director.must_change_password = False
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(director)}"}
    assert client.get("/api/students", headers=headers).status_code == 200
    assert client.post(
        "/api/admissions/leads",
        headers=headers,
        json={
            "student": "Read Only Attempt",
            "mobile": "9876543210",
            "parent": "Parent",
            "program": "JEE",
            "source": "walk-in",
            "counsellor": "Director",
            "nextAction": "Review",
        },
    ).status_code == 403


def test_owner_can_assign_per_user_module_actions(client, database, owner_headers):
    staff = User(
        mobile="9000000010",
        email="staff@example.com",
        full_name="Operations Staff",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add(staff)
    database.commit()
    staff_headers = {"Authorization": f"Bearer {create_token(staff)}"}

    updated = client.put(
        f"/api/settings/users/{staff.id}/permissions",
        json=permissions_payload(
            admissions={"read": True, "create": True, "edit": False},
            finance={"read": True, "create": False, "edit": False},
        ),
        headers=owner_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["permissions"]["admissions"] == {
        "read": True,
        "create": True,
        "edit": False,
    }
    assert database.query(UserModulePermission).filter_by(user_id=staff.id).count() == len(MODULES)

    assert client.get("/api/admissions/leads", headers=staff_headers).status_code == 200
    created = client.post(
        "/api/admissions/leads",
        json={
            "student": "Permission Test",
            "mobile": "9876543210",
            "parent": "Test Parent",
            "program": "JEE",
            "source": "walk-in",
            "counsellor": "Operations Staff",
            "nextAction": "Schedule counselling",
        },
        headers=staff_headers,
    )
    assert created.status_code == 201
    assert client.patch(
        f"/api/admissions/leads/{created.json()['id']}/stage",
        json={"stage": "Contacted"},
        headers=staff_headers,
    ).status_code == 403

    assert client.get("/api/finance/agreements", headers=staff_headers).status_code == 200
    assert client.post(
        "/api/finance/agreements",
        json={"studentId": "missing", "agreedAmount": 1000, "currency": "INR", "status": "active"},
        headers=staff_headers,
    ).status_code == 403
    assert client.get("/api/students", headers=staff_headers).status_code == 403

    me = client.get("/api/auth/me", headers=staff_headers)
    assert me.status_code == 200
    assert me.json()["permissions"]["finance"] == {
        "read": True,
        "create": False,
        "edit": False,
    }
    assert database.query(AuditLog).filter_by(action="settings.user.permissions.update", entity_id=staff.id).count() == 1


def test_owner_and_portal_permission_boundaries(client, database, owner_headers):
    owner = database.query(User).filter_by(role="owner").one()
    parent = database.query(User).filter_by(role="parent_student").one()
    payload = permissions_payload()

    assert client.put(
        f"/api/settings/users/{owner.id}/permissions",
        json=payload,
        headers=owner_headers,
    ).status_code == 409
    assert client.put(
        f"/api/settings/users/{parent.id}/permissions",
        json=payload,
        headers=owner_headers,
    ).status_code == 409
    assert client.delete(
        f"/api/settings/users/{owner.id}/permissions",
        headers=owner_headers,
    ).status_code == 409
    assert client.delete(
        f"/api/settings/users/{parent.id}/permissions",
        headers=owner_headers,
    ).status_code == 409


def test_owner_can_restore_recommended_role_access(client, database, owner_headers):
    staff = User(
        mobile="9000000013",
        full_name="Accounts Reset Test",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add(staff)
    database.commit()
    custom = client.put(
        f"/api/settings/users/{staff.id}/permissions",
        json=permissions_payload(admissions={"read": True, "create": True, "edit": True}),
        headers=owner_headers,
    )
    assert custom.status_code == 200
    assert database.query(UserModulePermission).filter_by(user_id=staff.id).count() == len(MODULES)

    restored = client.delete(
        f"/api/settings/users/{staff.id}/permissions",
        headers=owner_headers,
    )
    assert restored.status_code == 200
    assert restored.json() == {
        "userId": staff.id,
        "permissions": role_default_permissions("accounts"),
        "hasCustomPermissions": False,
    }
    assert database.query(UserModulePermission).filter_by(user_id=staff.id).count() == 0
    assert database.query(AuditLog).filter_by(
        action="settings.user.permissions.reset",
        entity_id=staff.id,
    ).count() == 1


def test_changing_role_removes_stale_custom_access(client, database, owner_headers):
    staff = User(
        mobile="9000000014",
        full_name="Role Change Test",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add(staff)
    database.commit()
    response = client.put(
        f"/api/settings/users/{staff.id}/permissions",
        json=permissions_payload(finance={"read": True, "create": True, "edit": True}),
        headers=owner_headers,
    )
    assert response.status_code == 200

    updated = client.patch(
        f"/api/settings/users/{staff.id}",
        json={
            "fullName": staff.full_name,
            "mobile": staff.mobile,
            "email": None,
            "role": "front_desk",
            "isActive": True,
        },
        headers=owner_headers,
    )
    assert updated.status_code == 200
    assert updated.json()["hasCustomPermissions"] is False
    assert updated.json()["permissions"] == role_default_permissions("front_desk")
    assert database.query(UserModulePermission).filter_by(user_id=staff.id).count() == 0


def test_mutating_permissions_require_view_access(client, database, owner_headers):
    staff = User(
        mobile="9000000011",
        full_name="Restricted Staff",
        role="front_desk",
        password_hash=hash_password("Password123!"),
    )
    database.add(staff)
    database.commit()
    invalid = permissions_payload(
        students={"read": False, "create": True, "edit": False},
    )
    response = client.put(
        f"/api/settings/users/{staff.id}/permissions",
        json=invalid,
        headers=owner_headers,
    )
    assert response.status_code == 422


def test_new_modules_are_denied_for_older_custom_permission_sets(client, database):
    staff = User(
        mobile="9000000017",
        full_name="Legacy Custom Accounts",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add(staff)
    database.flush()
    database.add(UserModulePermission(
        user_id=staff.id,
        module="finance",
        can_read=True,
        can_create=False,
        can_edit=False,
    ))
    database.commit()

    headers = {"Authorization": f"Bearer {create_token(staff)}"}
    me = client.get("/api/auth/me", headers=headers)
    assert me.status_code == 200
    assert me.json()["permissions"]["finance"]["read"] is True
    assert me.json()["permissions"]["payroll"] == {
        "read": False,
        "create": False,
        "edit": False,
    }
    assert client.get("/api/payroll/bootstrap?month=2026-08", headers=headers).status_code == 403


def test_independent_academic_access_includes_required_reference_data(
    client,
    database,
    owner_headers,
):
    staff = User(
        mobile="9000000012",
        full_name="Academic Reader",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    batch = Batch(name="Tatva", program="JEE", is_active=True)
    subject = Subject(name="Physics", code="PHY", program="JEE", is_active=True)
    database.add_all([staff, batch, subject])
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(staff)}"}
    response = client.put(
        f"/api/settings/users/{staff.id}/permissions",
        json=permissions_payload(
            academics={"read": True, "create": False, "edit": False},
        ),
        headers=owner_headers,
    )
    assert response.status_code == 200

    references = client.get("/api/workspace/reference-data", headers=headers)
    assert references.status_code == 200
    assert references.json()["batches"] == [
        {"id": batch.id, "name": "Tatva", "program": "JEE"}
    ]
    assert references.json()["subjects"] == [
        {"id": subject.id, "name": "Physics", "code": "PHY", "program": "JEE"}
    ]
    assert client.get("/api/academics/assignments", headers=headers).status_code == 200
    assert client.get("/api/timetable/bootstrap", headers=headers).status_code == 403
