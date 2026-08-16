from datetime import datetime, timedelta, timezone

from app.models import (
    Assignment,
    Batch,
    ClassSession,
    Enrollment,
    FacultyTeachingAssignment,
    Room,
    Student,
    StudentAccount,
    StudentSubjectSelection,
    Subject,
    User,
)
from app.security import create_token, hash_password


def _headers(user):
    return {"Authorization": f"Bearer {create_token(user)}"}


def test_subject_rosters_stay_aligned_across_all_portals(
    client,
    database,
    owner_headers,
):
    owner = database.query(User).filter_by(role="owner").one()
    faculty = User(
        mobile="9888800001",
        full_name="Maths Faculty",
        role="faculty",
        password_hash=hash_password("Password123!"),
    )
    student_user = User(
        mobile="9888800002",
        full_name="Legacy Maths Student",
        role="student",
        password_hash=hash_password("Password123!"),
    )
    batch = Batch(name="Tatva", program="All programs")
    maths = Subject(name="Maths", code="MATH", program="All programs")
    room = Room(name="Room 101", capacity=50)
    legacy_maths_student = Student(
        admission_number="LI-2026-20001",
        full_name="Legacy Maths Student",
        status="active",
    )
    neet_maths_student = Student(
        admission_number="LI-2026-20002",
        full_name="NEET Maths Student",
        status="active",
    )
    physics_only_student = Student(
        admission_number="LI-2026-20003",
        full_name="Physics Only Student",
        status="active",
    )
    database.add_all([
        faculty,
        student_user,
        batch,
        maths,
        room,
        legacy_maths_student,
        neet_maths_student,
        physics_only_student,
    ])
    database.flush()
    database.add_all([
        Enrollment(
            student_id=legacy_maths_student.id,
            program="JEE",
            batch="Tatva",
            status="active",
            is_active=True,
        ),
        Enrollment(
            student_id=neet_maths_student.id,
            program="NEET",
            batch="Tatva",
            status="active",
            is_active=True,
        ),
        Enrollment(
            student_id=physics_only_student.id,
            program="JEE",
            batch="Tatva",
            status="active",
            is_active=True,
        ),
        StudentSubjectSelection(
            student_id=legacy_maths_student.id,
            subject_name="Mathematics",
            source_value="Mathematics",
        ),
        StudentSubjectSelection(
            student_id=neet_maths_student.id,
            subject_name="Maths",
            source_value="Maths",
        ),
        StudentSubjectSelection(
            student_id=physics_only_student.id,
            subject_name="Physics",
            source_value="Physics",
        ),
        StudentAccount(
            user_id=student_user.id,
            student_id=legacy_maths_student.id,
        ),
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=maths.id,
            created_by=owner.id,
        ),
    ])
    now = datetime.now(timezone.utc)
    database.add_all([
        ClassSession(
            batch_id=batch.id,
            subject_id=maths.id,
            faculty_id=faculty.id,
            room_id=room.id,
            starts_at=now + timedelta(days=1),
            ends_at=now + timedelta(days=1, hours=1),
            status="scheduled",
            created_by=owner.id,
        ),
        Assignment(
            batch_id=batch.id,
            subject_id=maths.id,
            title="Algebra practice",
            instructions="Complete the worksheet.",
            due_at=now + timedelta(days=2),
            external_url="https://example.com/algebra",
            status="published",
            created_by=faculty.id,
        ),
    ])
    database.commit()

    student_portal = client.get(
        "/api/portal/bootstrap",
        headers=_headers(student_user),
    )
    assert student_portal.status_code == 200
    assert student_portal.json()["profile"]["subjects"] == ["Maths"]
    assert [row["subject"] for row in student_portal.json()["schedule"]] == [
        "Maths",
    ]
    assert [row["subject"] for row in student_portal.json()["assignments"]] == [
        "Maths",
    ]

    operation_assignments = client.get(
        "/api/academics/assignments",
        headers=owner_headers,
    )
    assert operation_assignments.status_code == 200
    assert operation_assignments.json()[0]["recipientCount"] == 2
    progress = client.get(
        f"/api/academics/assignments/{operation_assignments.json()[0]['id']}/progress",
        headers=owner_headers,
    )
    assert progress.status_code == 200
    assert [row["fullName"] for row in progress.json()["students"]] == [
        "Legacy Maths Student",
        "NEET Maths Student",
    ]

    faculty_portal = client.get(
        "/api/faculty/bootstrap",
        headers=_headers(faculty),
    )
    assert faculty_portal.status_code == 200
    assert faculty_portal.json()["teachingPairs"][0]["studentCount"] == 2
    assert faculty_portal.json()["assignments"][0]["recipientCount"] == 2

    communication = client.get(
        "/api/communication/inbox",
        headers=_headers(student_user),
    )
    assert communication.status_code == 200
    assert [row["name"] for row in communication.json()["subjects"]] == ["Maths"]

    examination = client.post(
        "/api/examinations",
        headers=owner_headers,
        json={
            "name": "Maths Unit Test",
            "batchId": batch.id,
            "subjectId": maths.id,
            "facultyId": faculty.id,
            "scheduledAt": (now + timedelta(days=3)).isoformat(),
            "durationMinutes": 60,
            "maxMarks": 50,
            "passMarks": 20,
            "instructions": "Bring your stationery.",
            "status": "scheduled",
        },
    )
    assert examination.status_code == 201
    assert examination.json()["participantCount"] == 2
    exam_detail = client.get(
        f"/api/examinations/{examination.json()['id']}",
        headers=owner_headers,
    )
    assert [row["fullName"] for row in exam_detail.json()["students"]] == [
        "Legacy Maths Student",
        "NEET Maths Student",
    ]


def test_operations_normalizes_mathematics_when_student_is_created(
    client,
    owner_headers,
):
    response = client.post(
        "/api/students",
        headers=owner_headers,
        json={
            "fullName": "New Maths Student",
            "mobile": "9777700001",
            "secondaryMobile": "",
            "email": None,
            "previousSchool": "",
            "program": "JEE",
            "batch": "Tatva",
            "enrollmentDate": "2026-08-16",
            "subjects": ["Mathematics", "Physics"],
            "agreedAmount": 100000,
        },
    )
    assert response.status_code == 201
    detail = client.get(
        f"/api/students/{response.json()['id']}",
        headers=owner_headers,
    )
    assert detail.status_code == 200
    assert detail.json()["academicProfile"]["subjects"] == ["Maths", "Physics"]
