from datetime import datetime, timedelta, timezone

from app.models import (
    Assignment,
    AssignmentRecipient,
    AuditLog,
    Batch,
    ClassSession,
    Enrollment,
    FacultyTeachingAssignment,
    Notice,
    Room,
    Student,
    Subject,
    User,
)
from app.security import create_token, hash_password


def test_faculty_email_is_first_login_only_until_mobile_activation(client, database):
    faculty = User(
        email="first.login.faculty@example.com",
        full_name="First Login Faculty",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    database.add(faculty)
    database.commit()

    first_login = client.post(
        "/api/auth/login",
        json={
            "email": faculty.email,
            "password": "FacultyPass123!",
        },
    )
    assert first_login.status_code == 200
    assert first_login.json()["user"]["mobile"] is None
    headers = {
        "Authorization": f"Bearer {first_login.json()['access_token']}",
    }
    activated = client.post(
        "/api/faculty/activate-mobile",
        headers=headers,
        json={"mobile": "+91 98765 40001"},
    )
    assert activated.status_code == 200
    assert activated.json()["mobile"] == "9876540001"

    email_rejected = client.post(
        "/api/auth/login",
        json={
            "email": faculty.email,
            "password": "FacultyPass123!",
        },
    )
    assert email_rejected.status_code == 401
    assert email_rejected.json()["detail"] == "Invalid sign-in details"

    mobile_login = client.post(
        "/api/auth/login",
        json={
            "mobile": "9876540001",
            "password": "FacultyPass123!",
        },
    )
    assert mobile_login.status_code == 200
    assert mobile_login.json()["user"]["role"] == "faculty"
    assert database.query(AuditLog).filter_by(
        action="faculty.mobile.activate",
        entity_id=faculty.id,
    ).count() == 1


def test_faculty_mobile_activation_rejects_duplicates_and_other_roles(
    client,
    database,
    parent_headers,
):
    faculty = User(
        email="duplicate.mobile.faculty@example.com",
        full_name="Duplicate Mobile Faculty",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    database.add(faculty)
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(faculty)}"}

    duplicate = client.post(
        "/api/faculty/activate-mobile",
        headers=headers,
        json={"mobile": "9000000001"},
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "This mobile number is already assigned to another account"

    denied = client.post(
        "/api/faculty/activate-mobile",
        headers=parent_headers,
        json={"mobile": "9876540002"},
    )
    assert denied.status_code == 403


def test_faculty_bootstrap_is_scoped_and_actionable(client, database, parent_headers):
    owner = database.query(User).filter_by(role="owner").one()
    faculty = User(
        email="meera.faculty@example.com",
        full_name="Dr Meera Rao",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    other_faculty = User(
        email="other.faculty@example.com",
        full_name="Dr Kabir Shah",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    batch = Batch(name="JEE 2027 A", program="JEE")
    other_batch = Batch(name="NEET 2027 A", program="NEET")
    physics = Subject(name="Physics", code="PHY", program="JEE")
    chemistry = Subject(name="Chemistry", code="CHEM", program="NEET")
    room = Room(name="Room 201", capacity=50)
    student = Student(
        admission_number="LI-2026-10001",
        full_name="Aarav Sharma",
        mobile="9000000001",
        status="active",
    )
    database.add_all([
        faculty, other_faculty, batch, other_batch, physics, chemistry, room, student,
    ])
    database.flush()
    database.add(Enrollment(
        student_id=student.id,
        program=batch.program,
        batch=batch.name,
        status="active",
    ))
    now = datetime.now(timezone.utc)
    own_session = ClassSession(
        batch_id=batch.id,
        subject_id=physics.id,
        faculty_id=faculty.id,
        room_id=room.id,
        starts_at=now - timedelta(minutes=30),
        ends_at=now + timedelta(minutes=30),
        created_by=owner.id,
    )
    other_session = ClassSession(
        batch_id=other_batch.id,
        subject_id=chemistry.id,
        faculty_id=other_faculty.id,
        room_id=room.id,
        starts_at=now + timedelta(days=1),
        ends_at=now + timedelta(days=1, hours=1),
        created_by=owner.id,
    )
    database.add_all([
        own_session,
        other_session,
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=physics.id,
            created_by=owner.id,
        ),
        FacultyTeachingAssignment(
            faculty_id=other_faculty.id,
            batch_id=other_batch.id,
            subject_id=chemistry.id,
            created_by=owner.id,
        ),
    ])
    database.flush()
    assignment = Assignment(
        batch_id=batch.id,
        subject_id=physics.id,
        title="Kinematics worksheet",
        instructions="Complete questions 1–10",
        due_at=now + timedelta(days=3),
        external_url="https://example.com/worksheet.pdf",
        status="published",
        created_by=faculty.id,
    )
    database.add(assignment)
    database.flush()
    database.add_all([
        Notice(
            title="Faculty meeting",
            body="Staff room at 5 PM.",
            audience="faculty",
            status="published",
            published_at=now,
            created_by=owner.id,
        ),
        Notice(
            title="Student notice",
            body="This should not appear.",
            audience="students",
            batch_id=batch.id,
            status="published",
            published_at=now,
            created_by=owner.id,
        ),
    ])
    database.commit()

    headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    response = client.get("/api/faculty/bootstrap", headers=headers)
    assert response.status_code == 200
    body = response.json()
    assert body["profile"]["fullName"] == "Dr Meera Rao"
    assert [row["id"] for row in body["sessions"]] == [own_session.id]
    assert body["sessions"][0]["studentCount"] == 1
    assert "registerStatus" not in body["sessions"][0]
    assert body["summary"] == {
        "todayClasses": 1,
        "openAssignments": 1,
        "activeBatches": 1,
    }
    assert [row["title"] for row in body["assignments"]] == ["Kinematics worksheet"]
    assert body["assignments"][0]["recipientCount"] == 1
    assert [row["title"] for row in body["notices"]] == ["Faculty meeting"]
    assert body["teachingPairs"][0]["subjectCode"] == "PHY"
    assert client.get("/api/faculty/bootstrap", headers=parent_headers).status_code == 403


def test_faculty_can_publish_only_their_own_draft_assignment(client, database):
    owner = database.query(User).filter_by(role="owner").one()
    faculty = User(
        email="draft.owner@example.com",
        full_name="Prof Anaya Deshmukh",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    other_faculty = User(
        email="draft.other@example.com",
        full_name="Prof Rohan Kulkarni",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    batch = Batch(name="JEE 2028 A", program="JEE")
    subject = Subject(name="Mathematics", code="MAT", program="JEE")
    room = Room(name="Room 301", capacity=45)
    student = Student(
        admission_number="LI-2026-11001",
        full_name="Ira Joshi",
        mobile="9000000011",
        status="active",
    )
    database.add_all([faculty, other_faculty, batch, subject, room, student])
    database.flush()
    database.add_all([
        Enrollment(
            student_id=student.id,
            program=batch.program,
            batch=batch.name,
            status="active",
        ),
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
            created_by=owner.id,
        ),
    ])
    database.commit()
    faculty_headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    other_headers = {"Authorization": f"Bearer {create_token(other_faculty)}"}
    created = client.post(
        "/api/academics/assignments",
        headers=faculty_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Quadratic equations draft",
            "instructions": "Complete questions 1–12.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=5)).isoformat(),
            "externalUrl": "https://example.com/quadratics.pdf",
            "status": "draft",
        },
    )
    assert created.status_code == 201
    assignment_id = created.json()["id"]
    assert created.json()["recipientCount"] == 1
    assert database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
    ).count() == 0
    denied = client.post(
        f"/api/academics/assignments/{assignment_id}/publish",
        headers=other_headers,
    )
    assert denied.status_code == 403
    denied_edit = client.patch(
        f"/api/academics/assignments/{assignment_id}",
        headers=other_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Unauthorised change",
            "instructions": "This must not be saved.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=6)).isoformat(),
            "externalUrl": "https://example.com/other.pdf",
            "status": "draft",
        },
    )
    assert denied_edit.status_code == 403
    edited = client.patch(
        f"/api/academics/assignments/{assignment_id}",
        headers=faculty_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Quadratic equations review",
            "instructions": "Complete questions 1–15.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=6)).isoformat(),
            "externalUrl": "https://example.com/quadratics-review.pdf",
            "status": "draft",
        },
    )
    assert edited.status_code == 200
    assert edited.json()["title"] == "Quadratic equations review"
    published = client.post(
        f"/api/academics/assignments/{assignment_id}/publish",
        headers=faculty_headers,
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert published.json()["recipientCount"] == 1
    assert database.get(Assignment, assignment_id).status == "published"
    assert database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
    ).count() == 0
    assert database.query(AuditLog).filter_by(
        action="academics.assignment.publish",
        entity_id=assignment_id,
    ).count() == 1
