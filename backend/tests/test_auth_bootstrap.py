from app.models import User


def test_first_owner_can_bootstrap_an_empty_workspace(client, database):
    database.query(User).delete()
    database.commit()

    assert client.get("/api/auth/bootstrap-status").json() == {
        "setupRequired": True,
        "allowLegacyEmailLogin": True,
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
    }
    assert client.get("/api/auth/bootstrap-status").json() == {
        "setupRequired": False,
        "allowLegacyEmailLogin": True,
    }

    duplicate = client.post(
        "/api/auth/bootstrap",
        json={"fullName": "Second Owner", "mobile": "9876543211", "password": "SecurePass123!"},
    )
    assert duplicate.status_code == 409
    assert database.query(User).count() == 1


def test_frontend_shell_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert '<h2 id="auth-title">Sign in</h2>' in response.text
    assert "Students" in response.text
    assert 'id="new-faculty-access"' in response.text
    assert 'id="new-attendance-access"' in response.text
    assert 'id="settings-faculty-access"' in response.text
    assert 'id="settings-attendance-access"' in response.text
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


def test_every_application_uses_a_mobile_login_field(client):
    for path in ("/", "/student-app/", "/parent-app/", "/faculty-app/", "/attendance-app/"):
        response = client.get(path)
        assert response.status_code == 200
        assert "Mobile number" in response.text
        assert 'name="mobile"' in response.text
        assert 'inputmode="tel"' in response.text
        assert "Email address" not in response.text


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


def test_legacy_email_login_remains_available_during_mobile_migration(client):
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
    assert response.json()["detail"] == "Invalid mobile number or password"


def test_invalid_mobile_is_rejected_without_account_lookup(client):
    response = client.post(
        "/api/auth/login",
        json={"mobile": "12345", "password": "Password123!"},
    )
    assert response.status_code == 422
