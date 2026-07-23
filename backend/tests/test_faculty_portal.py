from datetime import datetime, timedelta, timezone

from app.models import (
    Assignment,
    AssignmentRecipient,
    AuditLog,
    AttendanceRegister,
    Batch,
    ClassSession,
    Enrollment,
    Notice,
    Room,
    Student,
    Subject,
    User,
)
from app.security import create_token, hash_password


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
    database.add_all([own_session, other_session])
    database.flush()
    database.add(AttendanceRegister(
        class_session_id=own_session.id,
        status="draft",
    ))
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
    assert body["sessions"][0]["registerStatus"] == "draft"
    assert body["summary"] == {
        "todayClasses": 1,
        "attendanceActions": 1,
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
        ClassSession(
            batch_id=batch.id,
            subject_id=subject.id,
            faculty_id=faculty.id,
            room_id=room.id,
            starts_at=datetime.now(timezone.utc) + timedelta(days=1),
            ends_at=datetime.now(timezone.utc) + timedelta(days=1, hours=1),
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
