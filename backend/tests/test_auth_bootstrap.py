from app.models import User


def test_first_owner_can_bootstrap_an_empty_workspace(client, database):
    database.query(User).delete()
    database.commit()

    assert client.get("/api/auth/bootstrap-status").json() == {"setupRequired": True}
    created = client.post(
        "/api/auth/bootstrap",
        json={"fullName": "Lakshya Director", "email": "director@lakshya.edu", "password": "SecurePass123!"},
    )
    assert created.status_code == 201
    assert created.json()["token_type"] == "bearer"
    assert client.get("/api/auth/bootstrap-status").json() == {"setupRequired": False}

    duplicate = client.post(
        "/api/auth/bootstrap",
        json={"fullName": "Second Owner", "email": "second@lakshya.edu", "password": "SecurePass123!"},
    )
    assert duplicate.status_code == 409
    assert database.query(User).count() == 1


def test_frontend_shell_is_served(client):
    response = client.get("/")
    assert response.status_code == 200
    assert '<h2 id="auth-title">Sign in</h2>' in response.text
    assert "Students" in response.text
    assert 'property="og:image" content="https://lakshyaedutech.onrender.com/share-card.png?v=2"' in response.text

    share_card = client.get("/share-card.png")
    assert share_card.status_code == 200
    assert share_card.headers["content-type"] == "image/png"


def test_health_checks_support_get_and_head(client):
    for path in ("/health", "/api/health"):
        response = client.get(path)
        assert response.status_code == 200
        assert response.json() == {"status": "ok", "service": "lakshya-erp"}
        assert client.head(path).status_code == 200


def test_login_logout_revokes_the_active_token(client):
    logged_in = client.post(
        "/api/auth/login",
        json={"email": "owner@example.com", "password": "Password123!"},
    )
    assert logged_in.status_code == 200
    token = logged_in.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    assert client.post("/api/auth/logout", headers=headers).status_code == 204

    rejected = client.get("/api/auth/me", headers=headers)
    assert rejected.status_code == 401
    assert rejected.json()["detail"] == "Session has been signed out"
