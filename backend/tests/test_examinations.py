from datetime import datetime, timedelta, timezone

from app.models import (
    AuditLog,
    Batch,
    Enrollment,
    ExaminationParticipant,
    ExaminationResult,
    FacultyTeachingAssignment,
    Student,
    StudentAccount,
    Subject,
    User,
)
from app.security import create_token, hash_password


def examination_setup(db):
    faculty = User(
        email="physics.faculty@example.com",
        full_name="Dr Meera Rao",
        role="faculty",
        password_hash=hash_password("Password123!"),
    )
    second_faculty = User(
        email="other.faculty@example.com",
        full_name="Prof Arjun Shah",
        role="faculty",
        password_hash=hash_password("Password123!"),
    )
    student_user = User(
        email="exam.student@example.com",
        full_name="Aarav Sharma",
        role="student",
        password_hash=hash_password("Password123!"),
    )
    batch = Batch(name="JEE 2027 A", program="JEE")
    subject = Subject(name="Physics", code="PHY", program="JEE")
    first = Student(
        admission_number="LI-2026-00101",
        full_name="Aarav Sharma",
        status="active",
    )
    second = Student(
        admission_number="LI-2026-00102",
        full_name="Diya Mehta",
        status="active",
    )
    db.add_all([
        faculty,
        second_faculty,
        student_user,
        batch,
        subject,
        first,
        second,
    ])
    db.flush()
    db.add_all([
        Enrollment(
            student_id=first.id,
            program=batch.program,
            batch=batch.name,
            status="active",
            is_active=True,
        ),
        Enrollment(
            student_id=second.id,
            program=batch.program,
            batch=batch.name,
            status="active",
            is_active=True,
        ),
        StudentAccount(user_id=student_user.id, student_id=first.id),
    ])
    db.commit()
    return faculty, second_faculty, student_user, batch, subject, first, second


def exam_payload(faculty, batch, subject):
    return {
        "name": "Unit Test 01",
        "batchId": batch.id,
        "subjectId": subject.id,
        "facultyId": faculty.id,
        "scheduledAt": (
            datetime.now(timezone.utc) + timedelta(days=2)
        ).isoformat(),
        "durationMinutes": 90,
        "maxMarks": 100,
        "passMarks": 40,
        "instructions": "Bring a calculator.",
        "status": "scheduled",
    }


def test_examination_workflow_publishes_complete_results(
    client,
    database,
    owner_headers,
):
    faculty, _, student_user, batch, subject, first, second = examination_setup(
        database,
    )
    created = client.post(
        "/api/examinations",
        json=exam_payload(faculty, batch, subject),
        headers=owner_headers,
    )
    assert created.status_code == 201
    exam_id = created.json()["id"]
    assert created.json()["participantCount"] == 2
    assert created.json()["marksEntered"] == 0

    listed = client.get("/api/examinations", headers=owner_headers)
    assert listed.status_code == 200
    assert listed.json()[0]["name"] == "Unit Test 01"

    student_headers = {
        "Authorization": f"Bearer {create_token(student_user)}",
    }
    scheduled_portal = client.get(
        "/api/portal/bootstrap",
        headers=student_headers,
    )
    assert scheduled_portal.status_code == 200
    assert scheduled_portal.json()["summary"]["upcomingExams"] == 1
    assert scheduled_portal.json()["examinations"][0]["marksObtained"] is None

    partial = client.put(
        f"/api/examinations/{exam_id}/marks",
        json={
            "entries": [{
                "studentId": first.id,
                "resultStatus": "graded",
                "marksObtained": 78.5,
                "remarks": "Strong performance",
            }],
        },
        headers=owner_headers,
    )
    assert partial.status_code == 200
    assert partial.json()["marksEntered"] == 1
    blocked = client.post(
        f"/api/examinations/{exam_id}/publish",
        headers=owner_headers,
    )
    assert blocked.status_code == 409
    assert "1 pending" in blocked.json()["detail"]

    completed = client.put(
        f"/api/examinations/{exam_id}/marks",
        json={
            "entries": [{
                "studentId": second.id,
                "resultStatus": "absent",
                "marksObtained": None,
                "remarks": "Medical leave",
            }],
        },
        headers=owner_headers,
    )
    assert completed.status_code == 200
    assert completed.json()["marksEntered"] == 2

    published = client.post(
        f"/api/examinations/{exam_id}/publish",
        headers=owner_headers,
    )
    assert published.status_code == 200
    assert published.json()["status"] == "published"
    assert published.json()["averageMarks"] == 78.5

    portal = client.get("/api/portal/bootstrap", headers=student_headers)
    result = portal.json()["examinations"][0]
    assert result["marksObtained"] == 78.5
    assert result["percentage"] == 78.5
    assert result["qualified"] is True
    assert result["remarks"] == "Strong performance"

    immutable = client.patch(
        f"/api/examinations/{exam_id}",
        json=exam_payload(faculty, batch, subject),
        headers=owner_headers,
    )
    assert immutable.status_code == 409
    assert database.query(ExaminationResult).count() == 2
    assert database.query(AuditLog).filter_by(
        action="examinations.publish",
        entity_id=exam_id,
    ).count() == 1


def test_faculty_sees_only_assigned_examinations(
    client,
    database,
    owner_headers,
):
    faculty, second_faculty, _, batch, subject, first, _ = examination_setup(
        database,
    )
    created = client.post(
        "/api/examinations",
        json=exam_payload(faculty, batch, subject),
        headers=owner_headers,
    )
    exam_id = created.json()["id"]
    faculty_headers = {
        "Authorization": f"Bearer {create_token(faculty)}",
    }
    other_headers = {
        "Authorization": f"Bearer {create_token(second_faculty)}",
    }
    assert len(client.get("/api/examinations", headers=faculty_headers).json()) == 1
    assert client.get("/api/examinations", headers=other_headers).json() == []
    assert client.get(
        f"/api/examinations/{exam_id}",
        headers=other_headers,
    ).status_code == 403

    over_maximum = client.put(
        f"/api/examinations/{exam_id}/marks",
        json={
            "entries": [{
                "studentId": first.id,
                "resultStatus": "graded",
                "marksObtained": 101,
                "remarks": "",
            }],
        },
        headers=faculty_headers,
    )
    assert over_maximum.status_code == 422


def test_faculty_can_schedule_from_explicit_assignment_without_a_class(
    client,
    database,
):
    faculty, second_faculty, _, batch, subject, _, _ = examination_setup(
        database,
    )
    owner = database.query(User).filter_by(role="owner").one()
    database.add(
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
            created_by=owner.id,
        ),
    )
    database.commit()
    faculty_headers = {
        "Authorization": f"Bearer {create_token(faculty)}",
    }
    created = client.post(
        "/api/examinations",
        json=exam_payload(faculty, batch, subject),
        headers=faculty_headers,
    )
    assert created.status_code == 201
    denied = client.post(
        "/api/examinations",
        json=exam_payload(second_faculty, batch, subject),
        headers={
            "Authorization": f"Bearer {create_token(second_faculty)}",
        },
    )
    assert denied.status_code == 403


def test_examination_roster_is_fixed_at_creation(
    client,
    database,
    owner_headers,
):
    faculty, _, _, batch, subject, _, _ = examination_setup(database)
    created = client.post(
        "/api/examinations",
        json=exam_payload(faculty, batch, subject),
        headers=owner_headers,
    )
    exam_id = created.json()["id"]
    assert database.query(ExaminationParticipant).filter_by(
        exam_id=exam_id,
    ).count() == 2

    late_student = Student(
        admission_number="LI-2026-00103",
        full_name="Late Admission",
        status="active",
    )
    database.add(late_student)
    database.flush()
    database.add(
        Enrollment(
            student_id=late_student.id,
            program=batch.program,
            batch=batch.name,
            status="active",
            is_active=True,
        )
    )
    database.commit()

    detail = client.get(
        f"/api/examinations/{exam_id}",
        headers=owner_headers,
    )
    assert detail.status_code == 200
    assert detail.json()["participantCount"] == 2
    assert "Late Admission" not in {
        student["fullName"] for student in detail.json()["students"]
    }
