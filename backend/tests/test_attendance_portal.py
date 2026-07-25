from datetime import datetime, timedelta, timezone

from app.models import AttendanceEntry, AttendanceRegister, Batch, ClassSession, Enrollment, Room, Student, Subject, User
from app.security import create_token, hash_password


def setup_attendance_day(database):
    owner = database.query(User).filter_by(role="owner").one()
    operator = User(
        email="attendance.operator@example.com",
        full_name="Rohan Attendance",
        role="attendance_operator",
        password_hash=hash_password("AttendancePass123!"),
    )
    faculty = User(
        email="physics.faculty@example.com",
        full_name="Dr Meera Rao",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    batch = Batch(name="JEE 2027 A", program="JEE")
    subject = Subject(name="Physics", code="PHY", program="JEE")
    room = Room(name="Room 201", capacity=50)
    student = Student(
        admission_number="LI-2026-10001",
        full_name="Aarav Sharma",
        mobile="9000000001",
        status="active",
    )
    database.add_all([operator, faculty, batch, subject, room, student])
    database.flush()
    database.add(Enrollment(
        student_id=student.id,
        program=batch.program,
        batch=batch.name,
        status="active",
    ))
    now = datetime.now(timezone.utc)
    started = ClassSession(
        batch_id=batch.id,
        subject_id=subject.id,
        faculty_id=faculty.id,
        room_id=room.id,
        starts_at=now - timedelta(minutes=30),
        ends_at=now + timedelta(minutes=30),
        status="scheduled",
        created_by=owner.id,
    )
    upcoming = ClassSession(
        batch_id=batch.id,
        subject_id=subject.id,
        faculty_id=faculty.id,
        room_id=room.id,
        starts_at=now + timedelta(hours=1),
        ends_at=now + timedelta(hours=2),
        status="scheduled",
        created_by=owner.id,
    )
    database.add_all([started, upcoming])
    database.commit()
    return operator, faculty, student, started, upcoming


def test_attendance_operator_sees_all_classes_and_submits_register(client, database):
    operator, _, student, started, upcoming = setup_attendance_day(database)
    batch = database.query(Batch).filter_by(name="JEE 2027 A").one()
    second_student = Student(
        admission_number="LI-2026-10002",
        full_name="Zoya Khan",
        mobile="9000000002",
        status="active",
    )
    database.add(second_student)
    database.flush()
    database.add(Enrollment(
        student_id=second_student.id,
        program=batch.program,
        batch=batch.name,
        status="active",
    ))
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(operator)}"}

    bootstrap = client.get("/api/attendance/bootstrap", headers=headers)
    assert bootstrap.status_code == 200
    body = bootstrap.json()
    assert body["profile"]["role"] == "attendance_operator"
    assert {item["id"] for item in body["sessions"]} == {started.id, upcoming.id}
    assert body["summary"] == {
        "scheduled": 2,
        "pending": 1,
        "upcoming": 1,
        "submitted": 0,
    }

    roster = client.get(f"/api/attendance/sessions/{started.id}", headers=headers)
    assert roster.status_code == 200
    assert roster.json()["entries"][0]["studentId"] == student.id

    marks = {"entries": [{"studentId": student.id, "status": "present", "reason": ""}]}
    draft = client.put(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
        json=marks,
    )
    assert draft.status_code == 200
    assert draft.json()["status"] == "draft"

    incomplete = client.post(
        f"/api/attendance/sessions/{started.id}/submit",
        headers=headers,
        json=marks,
    )
    assert incomplete.status_code == 409
    assert "Every active student" in incomplete.json()["detail"]
    marks["entries"].append({
        "studentId": second_student.id,
        "status": "absent",
        "reason": "Medical leave",
    })
    submitted = client.post(
        f"/api/attendance/sessions/{started.id}/submit",
        headers=headers,
        json=marks,
    )
    assert submitted.status_code == 200
    assert submitted.json()["status"] == "submitted"
    register = database.query(AttendanceRegister).filter_by(
        class_session_id=started.id,
    ).one()
    assert register.submitted_by == operator.id
    assert database.query(AttendanceEntry).filter_by(
        register_id=register.id,
        student_id=student.id,
    ).one().marked_by == operator.id


def test_faculty_cannot_access_or_write_attendance(client, database):
    _, faculty, student, started, _ = setup_attendance_day(database)
    headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    marks = {"entries": [{"studentId": student.id, "status": "present", "reason": ""}]}

    assert client.get("/api/attendance/sessions", headers=headers).status_code == 403
    assert client.get(f"/api/attendance/sessions/{started.id}", headers=headers).status_code == 403
    assert client.put(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
        json=marks,
    ).status_code == 403
    assert client.post(
        f"/api/attendance/sessions/{started.id}/submit",
        headers=headers,
        json=marks,
    ).status_code == 403


def test_attendance_app_is_served(client):
    response = client.get("/attendance-app/")
    assert response.status_code == 200
    assert "Attendance Desk" in response.text


def test_owner_can_create_attendance_operator(client, owner_headers):
    response = client.post(
        "/api/settings/users",
        headers=owner_headers,
        json={
            "fullName": "Attendance Desk Operator",
            "email": "attendance.desk@example.com",
            "password": "AttendancePass123!",
            "role": "attendance_operator",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "attendance_operator"
