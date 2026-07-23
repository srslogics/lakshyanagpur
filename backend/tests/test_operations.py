from datetime import datetime, timedelta, timezone

from app.models import AssignmentRecipient, AuditLog, Batch, Enrollment, ParentAccount, Room, Student, StudentAccount, Subject, User
from app.security import create_token, hash_password


def operational_setup(db):
    faculty = User(email="faculty@example.com", full_name="Dr Meera Rao", role="faculty", password_hash=hash_password("Password123!"))
    batch = Batch(name="JEE 2027 A", program="JEE")
    other_batch = Batch(name="NEET 2027 A", program="NEET")
    subject = Subject(name="Physics", code="PHY", program="JEE")
    room = Room(name="Room 201", capacity=50)
    second_room = Room(name="Room 202", capacity=50)
    student = Student(admission_number="LI-2026-00001", full_name="Aarav Sharma", mobile="9000000001", status="active")
    other_student = Student(admission_number="LI-2026-00002", full_name="Diya Patel", mobile="9000000002", status="active")
    db.add_all([faculty, batch, other_batch, subject, room, second_room, student, other_student]); db.flush()
    db.add_all([Enrollment(student_id=student.id, program="JEE", batch=batch.name, status="active"), Enrollment(student_id=other_student.id, program="NEET", batch=other_batch.name, status="active")]); db.commit()
    return faculty, batch, subject, room, second_room, student, other_student


def session_payload(faculty, batch, subject, room, start=None):
    start = start or datetime.now(timezone.utc) + timedelta(days=1)
    return {"batchId": batch.id, "subjectId": subject.id, "facultyId": faculty.id, "roomId": room.id, "startsAt": start.isoformat(), "endsAt": (start + timedelta(hours=1)).isoformat(), "notes": "Mechanics"}


def test_timetable_rejects_conflicts_and_audits_override(client, database, owner_headers):
    faculty, batch, subject, room, second_room, *_ = operational_setup(database)
    start = datetime.now(timezone.utc) + timedelta(days=1)
    first = client.post("/api/timetable/sessions", json=session_payload(faculty, batch, subject, room, start), headers=owner_headers)
    assert first.status_code == 201
    conflicting = session_payload(faculty, batch, subject, second_room, start + timedelta(minutes=20))
    rejected = client.post("/api/timetable/sessions", json=conflicting, headers=owner_headers)
    assert rejected.status_code == 409
    assert rejected.json()["detail"]["code"] == "SCHEDULE_CONFLICT"
    conflicting.update({"allowOverride": True, "overrideReason": "Director-approved revision class"})
    overridden = client.post("/api/timetable/sessions", json=conflicting, headers=owner_headers)
    assert overridden.status_code == 201
    assert overridden.json()["overrideReason"] == "Director-approved revision class"
    assert database.query(AuditLog).filter_by(action="timetable.session.create").count() == 2


def test_assignment_uses_active_batch_without_recipient_fanout(client, database, owner_headers):
    _, batch, subject, *_ = operational_setup(database)
    response = client.post("/api/academics/assignments", json={"batchId": batch.id, "subjectId": subject.id, "title": "Kinematics practice", "instructions": "Complete all questions", "dueAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(), "externalUrl": "https://example.com/physics.pdf", "status": "published"}, headers=owner_headers)
    assert response.status_code == 201
    assert response.json()["recipientCount"] == 1
    recipients = database.query(AssignmentRecipient).filter_by(assignment_id=response.json()["id"]).all()
    assert recipients == []


def test_submitted_attendance_is_locked_and_corrections_are_audited(client, database, owner_headers, parent_headers):
    faculty, batch, subject, room, _, student, _ = operational_setup(database)
    scheduled = client.post(
        "/api/timetable/sessions",
        json=session_payload(
            faculty,
            batch,
            subject,
            room,
            datetime.now(timezone.utc) - timedelta(minutes=30),
        ),
        headers=owner_headers,
    )
    session_id = scheduled.json()["id"]
    marks = {"entries": [{"studentId": student.id, "status": "present", "reason": ""}]}
    submitted = client.post(f"/api/attendance/sessions/{session_id}/submit", json=marks, headers=owner_headers)
    assert submitted.status_code == 200
    locked = client.put(f"/api/attendance/sessions/{session_id}", json=marks, headers=owner_headers)
    assert locked.status_code == 409
    forbidden = client.post(f"/api/attendance/sessions/{session_id}/corrections/{student.id}", json={"status": "late", "reason": "Bus delay confirmed"}, headers=parent_headers)
    assert forbidden.status_code == 403
    corrected = client.post(f"/api/attendance/sessions/{session_id}/corrections/{student.id}", json={"status": "late", "reason": "Bus delay confirmed"}, headers=owner_headers)
    assert corrected.status_code == 200
    assert corrected.json()["status"] == "late"
    log = database.query(AuditLog).filter_by(action="attendance.correction").one()
    assert log.before["status"] == "present"
    assert log.after["status"] == "late"


def test_future_class_allows_draft_but_blocks_attendance_submission(client, database, owner_headers):
    faculty, batch, subject, room, _, student, _ = operational_setup(database)
    scheduled = client.post(
        "/api/timetable/sessions",
        json=session_payload(
            faculty,
            batch,
            subject,
            room,
            datetime.now(timezone.utc) + timedelta(days=1),
        ),
        headers=owner_headers,
    )
    session_id = scheduled.json()["id"]
    marks = {"entries": [{"studentId": student.id, "status": "present", "reason": ""}]}
    draft = client.put(
        f"/api/attendance/sessions/{session_id}",
        json=marks,
        headers=owner_headers,
    )
    assert draft.status_code == 200
    blocked = client.post(
        f"/api/attendance/sessions/{session_id}/submit",
        json=marks,
        headers=owner_headers,
    )
    assert blocked.status_code == 409
    assert "after the class begins" in blocked.json()["detail"]


def test_settings_are_owner_only(client, database, owner_headers, parent_headers):
    denied = client.get("/api/settings/bootstrap", headers=parent_headers)
    assert denied.status_code == 403
    created = client.post("/api/settings/rooms", json={"name": "Lab 1", "capacity": 36}, headers=owner_headers)
    assert created.status_code == 201
    assert created.json()["capacity"] == 36


def test_student_portal_returns_only_the_linked_student(client, database, owner_headers, parent_headers):
    faculty, batch, subject, room, _, student, other_student = operational_setup(database)
    parent = database.query(User).filter_by(role="parent_student").one()
    database.add(StudentAccount(user_id=parent.id, student_id=student.id)); database.commit()
    scheduled = client.post("/api/timetable/sessions", json=session_payload(faculty, batch, subject, room), headers=owner_headers)
    assert scheduled.status_code == 201
    assignment = client.post("/api/academics/assignments", json={"batchId": batch.id, "subjectId": subject.id, "title": "Portal practice", "instructions": "Complete the worksheet", "dueAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(), "externalUrl": "https://example.com/work.pdf", "status": "published"}, headers=owner_headers)
    assert assignment.status_code == 201
    portal = client.get("/api/portal/bootstrap", headers=parent_headers)
    assert portal.status_code == 200
    body = portal.json()
    assert body["account"]["email"] == parent.email
    assert body["profile"]["id"] == student.id
    assert body["profile"]["id"] != other_student.id
    assert [item["title"] for item in body["assignments"]] == ["Portal practice"]
    assert body["schedule"][0]["subject"] == "Physics"
    assert client.get("/api/portal/bootstrap", headers=owner_headers).status_code == 403


def test_student_added_to_batch_after_publication_sees_assignment_without_backfill(client, database, owner_headers):
    _, batch, subject, *_ = operational_setup(database)
    assignment = client.post(
        "/api/academics/assignments",
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Batch revision sheet",
            "instructions": "Complete the revision sheet.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "externalUrl": "https://example.com/revision.pdf",
            "status": "published",
        },
        headers=owner_headers,
    )
    assert assignment.status_code == 201
    late_student = Student(
        admission_number="LI-2026-00003",
        full_name="Riya Mehta",
        mobile="9000000003",
        status="active",
    )
    late_user = User(
        email="riya.student@example.com",
        full_name=late_student.full_name,
        role="student",
        password_hash=hash_password("StudentPass123!"),
    )
    database.add_all([late_student, late_user])
    database.flush()
    database.add_all([
        Enrollment(
            student_id=late_student.id,
            program=batch.program,
            batch=batch.name,
            status="active",
        ),
        StudentAccount(user_id=late_user.id, student_id=late_student.id),
    ])
    database.commit()
    portal = client.get(
        "/api/portal/bootstrap",
        headers={"Authorization": f"Bearer {create_token(late_user)}"},
    )
    assert portal.status_code == 200
    assert [item["title"] for item in portal.json()["assignments"]] == [
        "Batch revision sheet"
    ]
    assert database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment.json()["id"],
    ).count() == 0


def test_student_can_update_only_their_assignment_status(client, database, owner_headers, parent_headers):
    faculty, batch, subject, _, _, student, other_student = operational_setup(database)
    student_user = database.query(User).filter_by(role="parent_student").one()
    database.add(StudentAccount(user_id=student_user.id, student_id=student.id))
    database.commit()
    assignment = client.post(
        "/api/academics/assignments",
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Student-owned practice",
            "instructions": "Complete the worksheet",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "externalUrl": "https://example.com/work.pdf",
            "status": "published",
        },
        headers=owner_headers,
    )
    assert assignment.status_code == 201
    assignment_id = assignment.json()["id"]

    completed = client.patch(
        f"/api/portal/assignments/{assignment_id}/status",
        json={"status": "completed"},
        headers=parent_headers,
    )
    assert completed.status_code == 200
    assert completed.json()["status"] == "completed"
    portal = client.get("/api/portal/bootstrap", headers=parent_headers)
    assert portal.status_code == 200
    assert portal.json()["summary"]["openAssignments"] == 0
    assert portal.json()["assignments"][0]["status"] == "completed"
    recipient = database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
        student_id=student.id,
    ).one()
    assert recipient.status == "completed"
    assert database.query(AuditLog).filter_by(
        action="portal.assignment.status",
        entity_id=f"{assignment_id}:{student.id}",
    ).count() == 1
    reopened = client.patch(
        f"/api/portal/assignments/{assignment_id}/status",
        json={"status": "published"},
        headers=parent_headers,
    )
    assert reopened.status_code == 200
    assert reopened.json()["status"] == "published"
    assert database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
        student_id=student.id,
    ).count() == 0
    portal = client.get("/api/portal/bootstrap", headers=parent_headers)
    assert portal.json()["summary"]["openAssignments"] == 1
    assert portal.json()["assignments"][0]["status"] == "published"
    assert database.query(AuditLog).filter_by(
        action="portal.assignment.status",
        entity_id=f"{assignment_id}:{student.id}",
    ).count() == 2

    other_user = User(
        email="other.student@example.com",
        full_name=other_student.full_name,
        role="student",
        password_hash=hash_password("OtherStudentPass123!"),
    )
    database.add(other_user)
    database.flush()
    database.add(StudentAccount(user_id=other_user.id, student_id=other_student.id))
    database.commit()
    other_headers = {"Authorization": f"Bearer {create_token(other_user)}"}
    denied = client.patch(
        f"/api/portal/assignments/{assignment_id}/status",
        json={"status": "completed"},
        headers=other_headers,
    )
    assert denied.status_code == 404


def test_owner_can_provision_one_portal_account_per_student(client, database, owner_headers):
    _, _, _, _, _, student, _ = operational_setup(database)
    payload = {"studentId": student.id, "email": "aarav.student@example.com", "password": "StudentPass123!"}
    created = client.post("/api/settings/student-access", json=payload, headers=owner_headers)
    assert created.status_code == 201
    assert created.json()["studentId"] == student.id
    duplicate = client.post("/api/settings/student-access", json={**payload, "email": "second@example.com"}, headers=owner_headers)
    assert duplicate.status_code == 409
    account = database.query(StudentAccount).filter_by(student_id=student.id).one()
    assert database.get(User, account.user_id).role == "student"


def test_parent_portal_uses_a_separate_contact_account(client, database, owner_headers):
    faculty, batch, subject, room, _, student, other_student = operational_setup(database)
    parent = User(
        email="aarav.parent@example.com",
        full_name="Asha Sharma",
        role="parent",
        password_hash=hash_password("ParentPass123!"),
    )
    database.add(parent)
    database.flush()
    database.add(ParentAccount(
        user_id=parent.id,
        student_id=student.id,
        contact_type="primary_contact",
    ))
    database.commit()

    scheduled = client.post(
        "/api/timetable/sessions",
        json=session_payload(faculty, batch, subject, room),
        headers=owner_headers,
    )
    assert scheduled.status_code == 201

    parent_headers = {"Authorization": f"Bearer {create_token(parent)}"}
    response = client.get("/api/parent/bootstrap", headers=parent_headers)
    assert response.status_code == 200
    body = response.json()
    assert body["account"] == {
        "id": parent.id,
        "fullName": "Asha Sharma",
        "email": "aarav.parent@example.com",
        "contactType": "primary_contact",
    }
    assert body["profile"]["id"] == student.id
    assert body["profile"]["id"] != other_student.id
    assert body["schedule"][0]["subject"] == "Physics"
    assert client.get("/api/portal/bootstrap", headers=parent_headers).status_code == 403


def test_owner_can_provision_parent_access_without_a_guardian_relationship(client, database, owner_headers):
    _, _, _, _, _, student, _ = operational_setup(database)
    response = client.post(
        "/api/settings/parent-access",
        json={
            "studentId": student.id,
            "fullName": "Asha Sharma",
            "email": "asha.parent@example.com",
            "password": "ParentPass123!",
            "contactType": "primary_contact",
        },
        headers=owner_headers,
    )
    assert response.status_code == 201
    assert response.json()["studentId"] == student.id
    account = database.query(ParentAccount).filter_by(student_id=student.id).one()
    user = database.get(User, account.user_id)
    assert user.role == "parent"
    assert account.contact_type == "primary_contact"
