from app.models import Student, User
from app.security import hash_password


def _create_demo_account(database):
    account = User(
        id="usr_operations_demo",
        username="demo-erp",
        full_name="ERP Demo",
        role="demo",
        password_hash=hash_password("demo123"),
        must_change_password=False,
        is_active=True,
        is_test_account=False,
    )
    database.add(account)
    database.commit()
    return account


def test_demo_login_receives_only_synthetic_workspace(client, database):
    database.add(
        Student(
            admission_number="LIVE-PRIVATE-001",
            full_name="Private Client Student",
            mobile="9888888888",
            previous_school="Private Client School",
            status="active",
        )
    )
    _create_demo_account(database)
    database.commit()

    login = client.post(
        "/api/auth/login",
        json={"username": "demo-erp", "password": "demo123", "portal": "operations"},
    )
    assert login.status_code == 200
    assert login.json()["user"] == {
        "id": "usr_operations_demo",
        "username": "demo-erp",
        "mobile": None,
        "email": None,
        "fullName": "ERP Demo",
        "role": "demo",
        "mustChangePassword": False,
        "permissions": {
            "admissions": {"read": True, "create": False, "edit": False},
            "students": {"read": True, "create": False, "edit": False},
            "finance": {"read": True, "create": False, "edit": False},
            "payroll": {"read": True, "create": False, "edit": False},
            "attendance": {"read": True, "create": False, "edit": False},
            "academics": {"read": True, "create": False, "edit": False},
            "examinations": {"read": True, "create": False, "edit": False},
            "timetable": {"read": True, "create": False, "edit": False},
            "communication": {"read": True, "create": False, "edit": False},
            "inventory": {"read": True, "create": False, "edit": False},
            "reports": {"read": True, "create": False, "edit": False},
        },
    }

    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    workspace_response = client.get("/api/workspace/bootstrap", headers=headers)
    assert workspace_response.status_code == 200
    workspace = workspace_response.json()
    serialized = str(workspace)
    assert workspace["students"]
    assert all(item["fullName"].startswith("Demo Student ") for item in workspace["students"])
    assert all(item["mobile"] is None for item in workspace["students"])
    assert "Private Client Student" not in serialized
    assert "9888888888" not in serialized
    assert "Private Client School" not in serialized


def test_demo_account_cannot_call_live_or_mutating_endpoints(client, database):
    _create_demo_account(database)
    login = client.post(
        "/api/auth/login",
        json={"username": "demo-erp", "password": "demo123"},
    )
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    assert client.get("/api/students", headers=headers).status_code == 403
    assert client.get("/api/workspace/reference-data", headers=headers).status_code == 403
    assert client.get("/api/settings/bootstrap", headers=headers).status_code == 403
    assert client.get("/api/push/config", headers=headers).status_code == 403
    assert client.post("/api/admissions/leads", headers=headers, json={}).status_code == 403
    assert client.post(
        "/api/auth/change-password",
        headers=headers,
        json={"currentPassword": "demo123", "newPassword": "changed123"},
    ).status_code == 403

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204


def test_demo_account_rejects_wrong_password(client, database):
    _create_demo_account(database)
    response = client.post(
        "/api/auth/login",
        json={"username": "demo-erp", "password": "wrong123"},
    )
    assert response.status_code == 401
