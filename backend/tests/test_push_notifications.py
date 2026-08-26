from app.models import PushSubscription, User
from app.push_notifications import _vapid_keys
from app.security import create_token
from py_vapid import Vapid02


def _headers(user):
    return {"Authorization": f"Bearer {create_token(user)}"}


def test_authenticated_portal_can_register_and_remove_its_device(client, database):
    student = database.query(User).filter_by(role="parent_student").one()
    student.role = "student"
    database.commit()
    endpoint = "https://push.example.test/subscriptions/student-device"
    registered = client.put(
        "/api/push/subscriptions",
        headers=_headers(student),
        json={
            "endpoint": endpoint,
            "keys": {"p256dh": "a" * 65, "auth": "b" * 24},
            "portal": "student",
            "userAgent": "test browser",
        },
    )
    assert registered.status_code == 200
    row = database.query(PushSubscription).one()
    assert row.user_id == student.id
    assert row.is_active is True

    wrong_portal = client.put(
        "/api/push/subscriptions",
        headers=_headers(student),
        json={
            "endpoint": "https://push.example.test/operations",
            "keys": {"p256dh": "a" * 65, "auth": "b" * 24},
            "portal": "operations",
        },
    )
    assert wrong_portal.status_code == 403

    removed = client.request(
        "DELETE",
        "/api/push/subscriptions",
        headers=_headers(student),
        json={"endpoint": endpoint},
    )
    assert removed.status_code == 200
    database.refresh(row)
    assert row.is_active is False


def test_push_config_exposes_a_valid_uncompressed_vapid_key(client, database):
    owner = database.query(User).filter_by(role="owner").one()
    response = client.get("/api/push/config", headers=_headers(owner))
    assert response.status_code == 200
    assert response.json()["available"] is True
    assert len(response.json()["publicKey"]) >= 86


def test_private_vapid_key_is_in_the_inline_format_expected_by_pywebpush():
    private_key, public_key = _vapid_keys()
    assert Vapid02.from_string(private_key) is not None
    assert len(public_key) == 87
