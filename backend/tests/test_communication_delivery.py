def test_in_app_notice_publishes_with_delivery_status(client, owner_headers):
    response = client.post(
        "/api/communication/notices",
        json={
            "title": "Holiday notice",
            "body": "The institute will remain closed tomorrow.",
            "audience": "all",
            "channel": "in_app",
            "status": "published",
        },
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["deliveryStatus"] == "delivered"


def test_external_channel_cannot_be_silently_published(client, owner_headers):
    response = client.post(
        "/api/communication/notices",
        json={
            "title": "Schedule update",
            "body": "Tomorrow's class starts at 10 AM.",
            "audience": "students",
            "channel": "whatsapp",
            "status": "published",
        },
        headers=owner_headers,
    )
    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "DELIVERY_PROVIDER_REQUIRED"

    draft = client.post(
        "/api/communication/notices",
        json={
            "title": "Schedule update",
            "body": "Tomorrow's class starts at 10 AM.",
            "audience": "students",
            "channel": "whatsapp",
            "status": "draft",
        },
        headers=owner_headers,
    )
    assert draft.status_code == 201
    assert draft.json()["deliveryStatus"] == "draft"


def test_channel_capabilities_are_explicit(client, owner_headers):
    response = client.get(
        "/api/communication/capabilities",
        headers=owner_headers,
    )
    assert response.status_code == 200
    channels = {item["id"]: item for item in response.json()["channels"]}
    assert channels["in_app"]["available"] is True
    assert channels["whatsapp"]["available"] is False

