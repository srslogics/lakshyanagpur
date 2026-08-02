from app.models import User
from app.security import hash_password


def test_first_owner_can_bootstrap_an_empty_workspace(client, database):
    database.query(User).delete()
    database.commit()

    assert client.get("/api/auth/bootstrap-status").json() == {
        "setupRequired": True,
        "allowLegacyEmailLogin": False,
    }
    created = client.post(
        "/api/auth/bootstrap",
        json={"fullName": "Lakshya Director", "mobile": "+91 98765 43210", "password": "SecurePass123!"},
    )
    assert created.status_code == 201
    assert created.json()["token_type"] == "bearer"
    assert created.json()["user"] == {
        "id": database.query(User).one().id,
        "mobile": "9876543210",
        "email": None,
        "fullName": "Lakshya Director",
        "role": "owner",
        "mustChangePassword": False,
    }
    assert client.get("/api/auth/bootstrap-status").json() == {
        "setupRequired": False,
        "allowLegacyEmailLogin": False,
    }

    duplicate = client.post(
        "/api/auth/bootstrap",
        json={"fullName": "Second Owner", "mobile": "9876543211", "password": "SecurePass123!"},
    )
    assert duplicate.status_code == 409
    assert database.query(User).count() == 1


def test_preloaded_non_owner_records_do_not_block_owner_setup(client, database):
    database.query(User).filter(User.role == "owner").delete()
    database.commit()
    assert database.query(User).count() > 0
    assert client.get("/api/auth/bootstrap-status").json()["setupRequired"] is True
    created = client.post(
        "/api/auth/bootstrap",
        json={
            "fullName": "Lakshya Director",
            "mobile": "9876543210",
            "password": "SecurePass123!",
        },
    )
    assert created.status_code == 201
    assert created.json()["user"]["role"] == "owner"


def test_frontend_shell_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert '<h2 id="auth-title">Sign in</h2>' in response.text
    assert "Students" in response.text
    assert 'id="settings-add-account"' in response.text
    assert 'id="settings-account-filter"' in response.text
    assert 'id="settings-accounts-panel"' in response.text
    assert 'id="settings-academics-panel"' in response.text
    assert 'property="og:image" content="https://lakshyaedutech.onrender.com/share-card.png?v=2"' in response.text

    share_card = client.get("/share-card.png")
    assert share_card.status_code == 200
    assert share_card.headers["content-type"] == "image/png"
    optimized_logo = client.get("/lakshya-logo-576.png")
    assert optimized_logo.status_code == 200
    assert len(optimized_logo.content) < len(client.get("/lakshya-logo.png").content)

    versioned_asset = client.get("/student-app/app.js?v=7")
    assert versioned_asset.status_code == 200
    assert "immutable" in versioned_asset.headers["cache-control"]
    assert client.get("/student-app/sw.js").headers["cache-control"] == "no-cache"


def test_frontend_and_api_responses_include_launch_security_headers(client):
    for path in ("/", "/student-app/", "/api/health"):
        response = client.get(path)
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["x-frame-options"] == "DENY"
        assert response.headers["referrer-policy"] == "strict-origin-when-cross-origin"
        assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
        policy = response.headers["content-security-policy"]
        assert "script-src 'self'" in policy
        assert "frame-ancestors 'none'" in policy
        assert "object-src 'none'" in policy

    secure = client.get("/", headers={"x-forwarded-proto": "https"})
    assert secure.headers["strict-transport-security"] == "max-age=31536000; includeSubDomains"


def test_unknown_and_sensitive_frontend_paths_return_not_found(client):
    for path in (
        "/this-route-does-not-exist",
        "/backend/app/main.py",
        "/render.yaml",
        "/README.md",
        "/.git/config",
    ):
        response = client.get(path)
        assert response.status_code == 404


def test_allowlisted_operations_routes_serve_the_app_shell(client):
    for path in (
        "/operations",
        "/operations/students",
        "/operations/finance",
        "/operations/students/stu_example",
        "/operations/finance/ledger/stu_example",
    ):
        response = client.get(path)
        assert response.status_code == 200
        assert '<div class="app-shell hidden" id="app-shell">' in response.text

    assert client.get("/operations/not-a-module").status_code == 404
    assert client.get("/operations/students/stu_example/private").status_code == 404


def test_allowlisted_root_assets_remain_public(client):
    for path in (
        "/index.html",
        "/app.js",
        "/styles.css",
        "/auth-shared.css",
        "/portal-shared.css",
        "/manifest.webmanifest",
        "/sw.js",
        "/share-card.png",
        "/lakshya-logo-576.png",
        "/pwa-icon-192.png",
    ):
        assert client.get(path).status_code == 200


def test_operations_home_exposes_role_aware_quick_actions(client):
    response = client.get("/")
    assert response.status_code == 200
    assert 'id="dashboard-quick-actions"' in response.text
    assert 'data-dashboard-action="lead"' in response.text
    assert 'data-dashboard-action="student"' in response.text
    assert 'data-dashboard-action="payment"' in response.text
    assert 'data-dashboard-action="session"' in response.text
    assert 'data-dashboard-action="notice"' in response.text
    assert "Daily work" in response.text
    assert "Administration" in response.text


def test_every_application_uses_a_mobile_login_field(client):
    for path in ("/", "/student-app/", "/parent-app/", "/faculty-app/", "/attendance-app/"):
        response = client.get(path)
        assert response.status_code == 200
        assert "Mobile number" in response.text
        assert 'name="mobile"' in response.text
        assert 'inputmode="tel"' in response.text
        assert "Email address" not in response.text


def test_every_password_field_has_an_accessible_visibility_control(client):
    app_paths = ("/", "/student-app/", "/parent-app/", "/faculty-app/", "/attendance-app/")
    script_paths = (
        "/app.js",
        "/student-app/app.js",
        "/parent-app/app.js",
        "/faculty-app/app.js",
        "/attendance-app/app.js",
    )

    for path in app_paths:
        response = client.get(path)
        assert response.status_code == 200
        assert response.text.count('type="password"') == response.text.count("data-password-toggle")
        assert response.text.count('aria-pressed="false"') >= response.text.count('type="password"')

    for path in script_paths:
        response = client.get(path)
        assert response.status_code == 200
        assert "function togglePassword" in response.text
        assert 'closest("[data-password-toggle]")' in response.text


def test_portal_service_workers_only_delete_their_own_old_caches(client):
    expected_prefixes = {
        "/sw.js": "lakshya-erp-app-",
        "/student-app/sw.js": "lakshya-student-",
        "/parent-app/sw.js": "lakshya-parent-",
        "/faculty-app/sw.js": "lakshya-faculty-",
        "/attendance-app/sw.js": "lakshya-attendance-",
    }
    for path, cache_prefix in expected_prefixes.items():
        response = client.get(path)
        assert response.status_code == 200
        assert f'key.startsWith("{cache_prefix}")' in response.text


def test_portal_manifests_keep_installations_inside_their_app(client):
    operations_manifest = client.get("/manifest.webmanifest").json()
    assert operations_manifest["start_url"] == "/operations"
    assert operations_manifest["scope"] == "/"

    expected_scopes = {
        "/student-app/manifest.webmanifest": "/student-app/",
        "/parent-app/manifest.webmanifest": "/parent-app/",
        "/faculty-app/manifest.webmanifest": "/faculty-app/",
        "/attendance-app/manifest.webmanifest": "/attendance-app/",
    }
    for path, scope in expected_scopes.items():
        manifest = client.get(path).json()
        assert manifest["start_url"] == scope
        assert manifest["scope"] == scope


def test_health_checks_support_get_and_head(client):
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "lakshya-erp"}
        assert client.head(path).status_code == 200


def test_login_logout_revokes_the_active_token(client):
    logged_in = client.post(
        "/api/auth/login",
        json={"mobile": "+91 90000 00001", "password": "Password123!"},
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["user"]["role"] == "owner"
    assert logged_in.json()["user"]["mobile"] == "9000000001"
    assert logged_in.json()["user"]["email"] == "owner@example.com"
    token = logged_in.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204

    rejected = client.get("/api/auth/me", headers=headers)
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "Session has been signed out"


def test_temporary_password_requires_replacement_and_revokes_the_session(
    client,
    database,
):
    user = User(
        mobile="9876540091",
        full_name="First Login Student",
        role="student",
        password_hash=hash_password("Lakshya@2026!"),
        must_change_password=True,
    )
    database.add(user)
    database.commit()
    login = client.post(
        "/api/auth/login",
        json={"mobile": user.mobile, "password": "Lakshya@2026!"},
    )
    assert login.status_code == 200
    assert login.json()["user"]["mustChangePassword"] is True
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    blocked = client.get("/api/portal/bootstrap", headers=headers)
    assert blocked.status_code == 403
    assert blocked.json()["detail"] == "Password change required"
    reused = client.post(
        "/api/auth/change-password",
        headers=headers,
        json={
            "currentPassword": "Lakshya@2026!",
            "newPassword": "Lakshya@2026!",
        },
    )
    assert reused.status_code == 400
    changed = client.post(
        "/api/auth/change-password",
        headers=headers,
        json={
            "currentPassword": "Lakshya@2026!",
            "newPassword": "PersonalPass456!",
        },
    )
    assert changed.status_code == 204
    assert client.get("/api/auth/me", headers=headers).status_code == 401
    replacement_login = client.post(
        "/api/auth/login",
        json={"mobile": user.mobile, "password": "PersonalPass456!"},
    )
    assert replacement_login.status_code == 200
    assert replacement_login.json()["user"]["mustChangePassword"] is False


def test_legacy_email_login_can_be_enabled_during_mobile_migration(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.auth.settings.allow_legacy_email_login",
        True,
    )
    logged_in = client.post(
        "/api/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert logged_in.status_code == 200
    assert logged_in.json()["user"]["mobile"] == "9000000001"


def test_legacy_email_login_can_be_disabled_after_migration(client, monkeypatch):
    monkeypatch.setattr(
        "app.routers.auth.settings.allow_legacy_email_login",
        False,
    )
    response = client.post(
        "/api/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid sign-in details"


def test_invalid_mobile_is_rejected_without_account_lookup(client):
    response = client.post(
        "/api/auth/login",
        json={"mobile": "12345", "password": "Password123!"},
    )
    assert response.status_code == 422


def test_repeated_failed_logins_are_temporarily_rate_limited(client):
    payload = {"mobile": "9888888888", "password": "WrongPassword123!"}
    for _ in range(8):
        assert client.post("/api/auth/login", json=payload).status_code == 401

    limited = client.post("/api/auth/login", json=payload)
    assert limited.status_code == 429
    assert int(limited.headers["retry-after"]) > 0
    assert limited.json()["detail"] == "Too many sign-in attempts. Please wait before trying again."
