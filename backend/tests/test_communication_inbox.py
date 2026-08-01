from app.models import (
    Batch,
    Enrollment,
    FacultyTeachingAssignment,
    ParentAccount,
    Student,
    StudentAccount,
    Subject,
    User,
)
from app.security import create_token, hash_password


def _headers(user):
    return {"Authorization": f"Bearer {create_token(user)}"}


def _communication_accounts(db):
    student_user = db.query(User).filter_by(role="parent_student").one()
    student_user.full_name = "Kamal Student"
    parent = User(
        mobile="9000000010",
        full_name="Kamal Parent",
        role="parent",
        password_hash=hash_password("Password123!"),
    )
    faculty = User(
        mobile="9000000011",
        full_name="Physics Faculty",
        role="faculty",
        password_hash=hash_password("Password123!"),
    )
    unrelated_faculty = User(
        mobile="9000000012",
        full_name="Other Faculty",
        role="faculty",
        password_hash=hash_password("Password123!"),
    )
    student = Student(
        admission_number="LI-2026-00001",
        full_name="Kamal Student",
        status="active",
    )
    batch = Batch(name="Tatva", program="JEE", is_active=True)
    subject = Subject(name="Physics", code="PHY", program="JEE", is_active=True)
    db.add_all([parent, faculty, unrelated_faculty, student, batch, subject])
    db.flush()
    db.add_all([
        StudentAccount(user_id=student_user.id, student_id=student.id),
        ParentAccount(user_id=parent.id, student_id=student.id, contact_type="primary_contact"),
        Enrollment(
            student_id=student.id,
            program="JEE",
            batch="Tatva",
            status="active",
            is_active=True,
        ),
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
            is_active=True,
        ),
    ])
    db.commit()
    return student_user, parent, faculty, unrelated_faculty, subject


def test_student_subject_message_reaches_operations_and_assigned_faculty(client, database, owner_headers):
    student, _, faculty, unrelated_faculty, subject = _communication_accounts(database)
    created = client.post(
        "/api/communication/threads",
        json={
            "subjectId": subject.id,
            "topic": "Physics doubt",
            "body": "Please explain the next doubt-solving slot.",
        },
        headers=_headers(student),
    )
    assert created.status_code == 201
    thread_id = created.json()["id"]

    operations = client.get("/api/communication/inbox", headers=owner_headers)
    assert operations.status_code == 200
    assert [row["id"] for row in operations.json()["threads"]] == [thread_id]

    faculty_inbox = client.get("/api/communication/inbox", headers=_headers(faculty))
    assert faculty_inbox.status_code == 200
    assert [row["id"] for row in faculty_inbox.json()["threads"]] == [thread_id]
    assert faculty_inbox.json()["canAnnounce"] is False

    hidden = client.get(
        f"/api/communication/threads/{thread_id}",
        headers=_headers(unrelated_faculty),
    )
    assert hidden.status_code == 404

    reply = client.post(
        f"/api/communication/threads/{thread_id}/messages",
        json={"body": "Your assigned Physics faculty will cover this tomorrow."},
        headers=_headers(faculty),
    )
    assert reply.status_code == 201
    detail = client.get(
        f"/api/communication/threads/{thread_id}",
        headers=_headers(student),
    ).json()
    assert len(detail["messages"]) == 2
    assert detail["messages"][-1]["senderRole"] == "faculty"


def test_parent_office_message_reaches_operations_but_not_faculty(client, database, owner_headers):
    _, parent, faculty, _, _ = _communication_accounts(database)
    created = client.post(
        "/api/communication/threads",
        json={
            "subjectId": None,
            "topic": "Document update",
            "body": "Please confirm whether the submitted document is recorded.",
        },
        headers=_headers(parent),
    )
    assert created.status_code == 201
    thread_id = created.json()["id"]
    assert client.get("/api/communication/inbox", headers=owner_headers).json()["threads"][0]["id"] == thread_id
    assert client.get("/api/communication/inbox", headers=_headers(faculty)).json()["threads"] == []


def test_faculty_cannot_publish_global_announcement(client, database):
    _, _, faculty, _, _ = _communication_accounts(database)
    response = client.post(
        "/api/communication/notices",
        json={
            "title": "Unauthorised global notice",
            "body": "Faculty must not publish this.",
            "audience": "all",
            "channel": "in_app",
            "status": "published",
        },
        headers=_headers(faculty),
    )
    assert response.status_code == 403


def test_operations_global_announcement_is_visible_in_every_portal(client, database, owner_headers):
    student, parent, faculty, _, _ = _communication_accounts(database)
    attendance_operator = User(
        mobile="9000000013",
        full_name="Attendance Desk",
        role="attendance_operator",
        password_hash=hash_password("Password123!"),
    )
    database.add(attendance_operator)
    database.commit()
    published = client.post(
        "/api/communication/notices",
        json={
            "title": "Institute-wide update",
            "body": "This announcement is visible in every portal.",
            "audience": "all",
            "channel": "in_app",
            "status": "published",
        },
        headers=owner_headers,
    )
    assert published.status_code == 201

    portal_requests = (
        ("/api/portal/bootstrap", student),
        ("/api/parent/bootstrap", parent),
        ("/api/faculty/bootstrap", faculty),
        ("/api/attendance/bootstrap", attendance_operator),
    )
    for path, user in portal_requests:
        response = client.get(path, headers=_headers(user))
        assert response.status_code == 200
        assert response.json()["notices"][0]["title"] == "Institute-wide update"


def test_operations_can_close_and_reopen_conversation(client, database, owner_headers):
    student, _, _, _, _ = _communication_accounts(database)
    thread_id = client.post(
        "/api/communication/threads",
        json={"subjectId": None, "topic": "Office help", "body": "Please help."},
        headers=_headers(student),
    ).json()["id"]
    closed = client.patch(
        f"/api/communication/threads/{thread_id}/status",
        json={"status": "closed"},
        headers=owner_headers,
    )
    assert closed.status_code == 200
    blocked_reply = client.post(
        f"/api/communication/threads/{thread_id}/messages",
        json={"body": "Another message"},
        headers=_headers(student),
    )
    assert blocked_reply.status_code == 409
    reopened = client.patch(
        f"/api/communication/threads/{thread_id}/status",
        json={"status": "open"},
        headers=owner_headers,
    )
    assert reopened.status_code == 200
