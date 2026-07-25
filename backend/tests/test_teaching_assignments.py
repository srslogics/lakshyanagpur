from app.models import Batch, FacultyTeachingAssignment, Subject, User
from app.security import create_token, hash_password


def test_owner_manages_explicit_teaching_assignments(
    client,
    database,
    owner_headers,
):
    faculty = User(
        email="assigned.faculty@example.com",
        full_name="Prof Kavya Nair",
        role="faculty",
        password_hash=hash_password("FacultyPass123!"),
    )
    batch = Batch(name="JEE 2029 A", program="JEE")
    subject = Subject(name="Physics", code="PHY-29", program="JEE")
    database.add_all([faculty, batch, subject])
    database.commit()

    created = client.post(
        "/api/timetable/teaching-assignments",
        headers=owner_headers,
        json={
            "facultyId": faculty.id,
            "batchId": batch.id,
            "subjectId": subject.id,
        },
    )
    assert created.status_code == 201
    assignment_id = created.json()["id"]
    assert created.json()["faculty"] == "Prof Kavya Nair"
    assert created.json()["sessionCount"] == 0

    duplicate = client.post(
        "/api/timetable/teaching-assignments",
        headers=owner_headers,
        json={
            "facultyId": faculty.id,
            "batchId": batch.id,
            "subjectId": subject.id,
        },
    )
    assert duplicate.status_code == 409

    bootstrap = client.get("/api/timetable/bootstrap", headers=owner_headers)
    assert bootstrap.status_code == 200
    assert bootstrap.json()["teachingAssignments"][0]["id"] == assignment_id

    disabled = client.patch(
        f"/api/timetable/teaching-assignments/{assignment_id}",
        headers=owner_headers,
        json={
            "facultyId": faculty.id,
            "batchId": batch.id,
            "subjectId": subject.id,
            "isActive": False,
        },
    )
    assert disabled.status_code == 200
    assert disabled.json()["isActive"] is False

    faculty_bootstrap = client.get(
        "/api/faculty/bootstrap",
        headers={"Authorization": f"Bearer {create_token(faculty)}"},
    )
    assert faculty_bootstrap.status_code == 200
    assert faculty_bootstrap.json()["teachingPairs"] == []
    assert database.query(FacultyTeachingAssignment).count() == 1
