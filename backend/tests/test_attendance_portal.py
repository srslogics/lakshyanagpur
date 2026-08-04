from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from app.models import (
    AcademicImportBatch,
    AttendanceEntry,
    AttendanceRegister,
    Batch,
    ClassSession,
    Enrollment,
    Room,
    Student,
    StudentAcademicProfile,
    StudentSubjectSelection,
    Subject,
    User,
)
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

    india_tz = ZoneInfo("Asia/Kolkata")
    selected_day = started.starts_at.astimezone(india_tz).date()
    bootstrap = client.get(
        f"/api/attendance/bootstrap?day={selected_day.isoformat()}",
        headers=headers,
    )
    assert bootstrap.status_code == 200
    body = bootstrap.json()
    assert body["profile"]["role"] == "attendance_operator"
    expected_sessions = {started.id}
    upcoming_in_selected_day = (
        upcoming.starts_at.astimezone(india_tz).date() == selected_day
    )
    if upcoming_in_selected_day:
        expected_sessions.add(upcoming.id)
    assert {item["id"] for item in body["sessions"]} == expected_sessions
    assert body["summary"] == {
        "scheduled": len(expected_sessions),
        "pending": 1,
        "upcoming": int(upcoming_in_selected_day),
        "submitted": 0,
    }

    roster = client.get(f"/api/attendance/sessions/{started.id}", headers=headers)
    assert roster.status_code == 200
    assert roster.json()["entries"][0]["studentId"] == student.id
    assert roster.json()["entries"][0]["arrivalAt"] is None

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
    present_entry = database.query(AttendanceEntry).filter_by(
        register_id=register.id,
        student_id=student.id,
    ).one()
    absent_entry = database.query(AttendanceEntry).filter_by(
        register_id=register.id,
        student_id=second_student.id,
    ).one()
    assert present_entry.arrival_at is not None
    assert absent_entry.arrival_at is None

    saved_roster = client.get(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
    ).json()
    saved_present = next(
        item for item in saved_roster["entries"]
        if item["studentId"] == student.id
    )
    assert saved_present["arrivalAt"] is not None


def test_attendance_preserves_supplied_arrival_time(client, database):
    operator, _, student, started, _ = setup_attendance_day(database)
    headers = {"Authorization": f"Bearer {create_token(operator)}"}
    arrival = (datetime.now(timezone.utc) - timedelta(minutes=12)).replace(
        microsecond=0,
    )
    marks = {
        "entries": [{
            "studentId": student.id,
            "status": "late",
            "reason": "Traffic delay",
            "arrivalAt": arrival.isoformat(),
        }],
    }

    saved = client.put(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
        json=marks,
    )
    assert saved.status_code == 200

    roster = client.get(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
    ).json()
    assert roster["entries"][0]["status"] == "late"
    assert datetime.fromisoformat(roster["entries"][0]["arrivalAt"]) == arrival

    marks["entries"][0].pop("arrivalAt")
    marks["entries"][0]["reason"] = "Updated note"
    assert client.put(
        f"/api/attendance/sessions/{started.id}",
        headers=headers,
        json=marks,
    ).status_code == 200
    preserved = database.query(AttendanceEntry).filter_by(
        student_id=student.id,
    ).one()
    assert preserved.arrival_at.replace(tzinfo=timezone.utc) == arrival


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


def test_class_roster_is_isolated_by_batch_and_program(client, database):
    operator, _, student, started, _ = setup_attendance_day(database)
    same_name_other_program = Batch(name="JEE 2027 A", program="NEET")
    other_student = Student(
        admission_number="LI-2026-10003",
        full_name="NEET Student In Same Group",
        mobile="9000000003",
        status="active",
    )
    database.add_all([same_name_other_program, other_student])
    database.flush()
    database.add(Enrollment(
        student_id=other_student.id,
        program="NEET",
        batch="JEE 2027 A",
        status="active",
    ))
    database.commit()
    headers = {"Authorization": f"Bearer {create_token(operator)}"}

    roster = client.get(f"/api/attendance/sessions/{started.id}", headers=headers)
    assert roster.status_code == 200
    assert roster.json()["session"]["studentCount"] == 1
    assert roster.json()["session"]["program"] == "JEE"
    assert [item["studentId"] for item in roster.json()["entries"]] == [student.id]


def setup_manual_attendance_catalog(database):
    operator = User(
        mobile="9000000094",
        full_name="Manual Attendance Operator",
        role="attendance_operator",
        password_hash=hash_password("AttendancePass123!"),
    )
    imported = AcademicImportBatch(
        source_name="Attendance workbook",
        source_hash="manual-attendance-catalog",
        status="completed",
        active_student_rows=3,
        attendance_entries=0,
        subject_selections=5,
        staged_source_rows=0,
        unresolved_items=0,
    )
    students = [
        Student(
            admission_number="LI-2026-M001",
            full_name="JEE Student",
            status="active",
        ),
        Student(
            admission_number="LI-2026-M002",
            full_name="NEET Student",
            status="active",
        ),
        Student(
            admission_number="LI-2026-M003",
            full_name="Boards Student",
            status="active",
        ),
    ]
    database.add_all([operator, imported, *students])
    database.flush()
    definitions = [
        (students[0], "Tatva", "JEE", ("Physics", "Chemistry")),
        (students[1], "Tatva", "NEET", ("Physics", "Biology")),
        (students[2], "Essential", "Boards", ("Physics",)),
    ]
    for index, (student, batch, stream, subjects) in enumerate(definitions, 1):
        database.add(Enrollment(
            student_id=student.id,
            program=stream,
            batch=batch,
            status="active",
            is_active=True,
        ))
        database.add(StudentAcademicProfile(
            student_id=student.id,
            source_student_code=f"MAN-{index:02d}",
            batch_name=batch,
            source_stream=stream,
            mentor_name=None,
            source_school_name=None,
            source_primary_mobile=None,
            source_secondary_mobile=None,
            import_batch_id=imported.id,
        ))
        for subject in subjects:
            database.add(StudentSubjectSelection(
                student_id=student.id,
                subject_name=subject,
                source_value=subject,
                import_batch_id=imported.id,
            ))
    database.commit()
    return operator, students


def test_operator_selects_only_group_for_manual_attendance(
    client,
    database,
):
    operator, students = setup_manual_attendance_catalog(database)
    headers = {"Authorization": f"Bearer {create_token(operator)}"}

    bootstrap = client.get("/api/attendance/bootstrap", headers=headers)
    assert bootstrap.status_code == 200
    catalog = bootstrap.json()["catalog"]
    assert catalog["studentCount"] == 3
    assert [item["name"] for item in catalog["groups"]] == [
        "Tatva",
        "Essential",
    ]
    tatva = next(item for item in catalog["groups"] if item["name"] == "Tatva")
    assert tatva["studentCount"] == 2
    assert [item["name"] for item in tatva["streams"]] == ["JEE", "NEET"]
    jee = next(item for item in tatva["streams"] if item["name"] == "JEE")
    assert jee["studentCount"] == 1
    assert {item["name"] for item in jee["subjects"]} == {
        "Chemistry",
        "Physics",
    }

    selection = {
        "date": date.today().isoformat(),
        "batch": "Tatva",
    }
    opened = client.post(
        "/api/attendance/manual-registers",
        headers=headers,
        json=selection,
    )
    assert opened.status_code == 200
    payload = opened.json()
    assert payload["session"]["registerKind"] == "manual"
    assert payload["session"]["studentCount"] == 2
    assert payload["session"]["stream"] == ""
    assert payload["session"]["subject"] == "Attendance"
    assert {item["studentId"] for item in payload["entries"]} == {
        students[0].id,
        students[1].id,
    }

    reopened = client.post(
        "/api/attendance/manual-registers",
        headers=headers,
        json=selection,
    )
    assert reopened.status_code == 200
    assert reopened.json()["session"]["id"] == payload["session"]["id"]

    submitted = client.post(
        f"/api/attendance/manual-registers/{payload['session']['id']}/submit",
        headers=headers,
        json={
            "entries": [
                {
                    "studentId": students[0].id,
                    "status": "present",
                    "reason": "",
                },
                {
                    "studentId": students[1].id,
                    "status": "present",
                    "reason": "",
                },
            ],
        },
    )
    assert submitted.status_code == 200
    register = database.get(AttendanceRegister, payload["session"]["id"])
    assert register.class_session_id is None
    assert register.register_kind == "manual"
    assert register.batch_name == "Tatva"
    assert register.stream_name == "__all__"
    assert register.subject_name == "Attendance"
    assert register.status == "submitted"
    from app.routers.portal import attendance_rows
    student_attendance = attendance_rows(database, students[0])
    manual_row = next(
        item for item in student_attendance
        if item["source"] == "manual_register"
    )
    assert manual_row["subject"] == "Attendance"
    assert manual_row["status"] == "present"


def test_attendance_app_is_served(client):
    response = client.get("/attendance-app/")
    assert response.status_code == 200
    assert "Attendance Desk" in response.text
    assert 'id="manual-register-form"' in response.text
    assert 'id="manual-batch"' in response.text
    assert 'id="manual-group-options"' in response.text
    assert 'id="manual-stream-options"' not in response.text
    assert 'id="manual-subject-options"' not in response.text
    assert "Choose a roster" in response.text


def test_legacy_attendance_links_redirect_to_the_attendance_app(client):
    for path in ("/attendence", "/attendence/", "/attendance", "/attendance/"):
        response = client.get(path, follow_redirects=False)
        assert response.status_code == 308
        assert response.headers["location"] == "/attendance-app/"


def test_owner_can_create_attendance_operator(client, owner_headers):
    response = client.post(
        "/api/settings/users",
        headers=owner_headers,
        json={
            "fullName": "Attendance Desk Operator",
            "mobile": "+91 90000 00091",
            "email": "attendance.desk@example.com",
            "password": "AttendancePass123!",
            "role": "attendance_operator",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "attendance_operator"
    assert response.json()["mobile"] == "9000000091"
    duplicate = client.post(
        "/api/settings/users",
        headers=owner_headers,
        json={
            "fullName": "Second Attendance Operator",
            "mobile": "9000000091",
            "password": "AttendancePass123!",
            "role": "attendance_operator",
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"] == "This mobile number is already assigned to another account"
