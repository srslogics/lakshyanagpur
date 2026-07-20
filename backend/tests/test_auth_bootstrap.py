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
    assert "Every student journey" in response.text
    assert "Student directory" in response.text
