from datetime import datetime, timedelta, timezone

from app.assignment_materials import MAX_ASSIGNMENT_PDF_BYTES
from app.models import (
    AssignmentDownload,
    AssignmentMaterial,
    AssignmentRecipient,
    Batch,
    Enrollment,
    FacultyTeachingAssignment,
    Student,
    StudentAccount,
    Subject,
    User,
)
from app.security import create_token, hash_password


def _assignment_setup(database):
    owner = database.query(User).filter_by(role="owner").one()
    student_user = database.query(User).filter_by(role="parent_student").one()
    faculty = User(
        mobile="9850242456",
        full_name="Jitendra Sir",
        role="faculty",
        password_hash=hash_password("Lakshaya@2026"),
    )
    batch = Batch(name="Essential", program="MHT-CET")
    subject = Subject(name="Chemistry", code="CHEM", program="All programs")
    student = Student(
        admission_number="LI-2026-12001",
        full_name="Riya Sharma",
        mobile="9000001201",
        status="active",
    )
    database.add_all([faculty, batch, subject, student])
    database.flush()
    database.add_all([
        Enrollment(
            student_id=student.id,
            program="MHT-CET",
            batch="Essential",
            status="active",
        ),
        StudentAccount(user_id=student_user.id, student_id=student.id),
        FacultyTeachingAssignment(
            faculty_id=faculty.id,
            batch_id=batch.id,
            subject_id=subject.id,
            created_by=owner.id,
        ),
    ])
    database.commit()
    return faculty, batch, subject, student


def test_assignment_pdf_download_is_counted_once_per_student_and_expires(
    client,
    database,
    parent_headers,
):
    assert MAX_ASSIGNMENT_PDF_BYTES == 15 * 1024 * 1024
    faculty, batch, subject, student = _assignment_setup(database)
    faculty_headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    created = client.post(
        "/api/academics/assignments",
        headers=faculty_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Atomic structure worksheet",
            "instructions": "Download and complete the worksheet.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "externalUrl": None,
            "status": "published",
        },
    )
    assert created.status_code == 201
    assignment_id = created.json()["id"]
    assert created.json()["externalUrl"] is None

    invalid = client.post(
        f"/api/academics/assignments/{assignment_id}/material",
        headers=faculty_headers,
        files={"file": ("notes.txt", b"not a PDF", "text/plain")},
    )
    assert invalid.status_code == 415

    uploaded = client.post(
        f"/api/academics/assignments/{assignment_id}/material",
        headers=faculty_headers,
        files={
            "file": (
                "chemistry worksheet.pdf",
                b"%PDF-1.4\n%%EOF\n",
                "application/pdf",
            ),
        },
    )
    assert uploaded.status_code == 200
    assert uploaded.json()["available"] is True
    assert uploaded.json()["downloadedCount"] == 0
    expires_at = datetime.fromisoformat(uploaded.json()["expiresAt"])
    assert timedelta(hours=47, minutes=59) < (
        expires_at - datetime.now(timezone.utc)
    ) <= timedelta(hours=48)

    bootstrap = client.get("/api/portal/bootstrap", headers=parent_headers)
    assert bootstrap.status_code == 200
    student_assignment = bootstrap.json()["assignments"][0]
    assert student_assignment["material"]["filename"] == "chemistry worksheet.pdf"

    first = client.get(
        f"/api/portal/assignments/{assignment_id}/material",
        headers=parent_headers,
    )
    second = client.get(
        f"/api/portal/assignments/{assignment_id}/material",
        headers=parent_headers,
    )
    assert first.status_code == second.status_code == 200
    assert first.content.startswith(b"%PDF-")
    assert "attachment" in first.headers["content-disposition"]
    download = database.query(AssignmentDownload).filter_by(
        assignment_id=assignment_id,
        student_id=student.id,
    ).one()
    assert download.download_count == 2
    assert database.query(AssignmentDownload).filter_by(
        assignment_id=assignment_id,
    ).count() == 1
    assert database.query(AssignmentRecipient).filter_by(
        assignment_id=assignment_id,
        student_id=student.id,
    ).one().status == "viewed"

    progress = client.get(
        f"/api/academics/assignments/{assignment_id}/progress",
        headers=faculty_headers,
    )
    assert progress.status_code == 200
    assert progress.json()["students"][0]["downloaded"] is True
    listed = client.get("/api/academics/assignments", headers=faculty_headers)
    assert listed.json()[0]["material"]["downloadedCount"] == 1
    assert listed.json()[0]["progress"]["downloaded"] == 1

    # Simulate retrying when the original upload's response never reached the phone.
    retried = client.post(
        f"/api/academics/assignments/{assignment_id}/material",
        headers=faculty_headers,
        files={"file": ("chemistry worksheet.pdf", b"%PDF-1.4\n%%EOF\n", "application/pdf")},
    )
    assert retried.status_code == 200
    assert retried.json()["expiresAt"] == uploaded.json()["expiresAt"]
    assert retried.json()["downloadedCount"] == 1
    database.expire_all()
    assert database.query(AssignmentDownload).filter_by(
        assignment_id=assignment_id, student_id=student.id,
    ).one().download_count == 2

    replaced = client.post(
        f"/api/academics/assignments/{assignment_id}/material",
        headers=faculty_headers,
        files={"file": ("revised.pdf", b"%PDF-1.4\nrevised\n", "application/pdf")},
    )
    assert replaced.status_code == 200
    assert replaced.json()["downloadedCount"] == 0
    assert database.query(AssignmentDownload).filter_by(
        assignment_id=assignment_id,
    ).count() == 0

    material = database.get(AssignmentMaterial, assignment_id)
    material.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
    database.commit()
    expired = client.get(
        f"/api/portal/assignments/{assignment_id}/material",
        headers=parent_headers,
    )
    assert expired.status_code == 404
    assert database.get(AssignmentMaterial, assignment_id) is None
    assert database.query(AssignmentDownload).filter_by(
        assignment_id=assignment_id,
    ).count() == 0


def test_faculty_cannot_upload_to_another_facultys_assignment(
    client,
    database,
    owner_headers,
):
    faculty, batch, subject, _ = _assignment_setup(database)
    created = client.post(
        "/api/academics/assignments",
        headers=owner_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Owner worksheet",
            "instructions": "Faculty must not replace this PDF.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "externalUrl": None,
            "status": "published",
        },
    )
    denied = client.post(
        f"/api/academics/assignments/{created.json()['id']}/material",
        headers={"Authorization": f"Bearer {create_token(faculty)}"},
        files={"file": ("worksheet.pdf", b"%PDF-1.4\n", "application/pdf")},
    )
    assert denied.status_code == 403


def test_assignment_pdf_accepts_15_mb_and_rejects_larger_files(client, database, parent_headers):
    faculty, batch, subject, _ = _assignment_setup(database)
    faculty_headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    created = client.post(
        "/api/academics/assignments",
        headers=faculty_headers,
        json={
            "batchId": batch.id,
            "subjectId": subject.id,
            "title": "Large worksheet",
            "instructions": "Confirm the production upload boundary.",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "externalUrl": None,
            "status": "published",
        },
    )
    assert created.status_code == 201

    pdf_header = b"%PDF-"
    oversized_pdf = pdf_header + b"x" * (
        MAX_ASSIGNMENT_PDF_BYTES - len(pdf_header) + 1
    )
    uploaded = client.post(
        f"/api/academics/assignments/{created.json()['id']}/material",
        headers=faculty_headers,
        files={"file": ("too-large.pdf", oversized_pdf, "application/pdf")},
    )
    assert uploaded.status_code == 413
    assert uploaded.json()["detail"] == "PDF must be 15 MB or smaller"

    accepted = client.post(
        f"/api/academics/assignments/{created.json()['id']}/material",
        headers=faculty_headers,
        files={"file": ("large.pdf", oversized_pdf[:-1], "application/pdf")},
    )
    assert accepted.status_code == 200
    assert accepted.json()["sizeBytes"] == MAX_ASSIGNMENT_PDF_BYTES
    downloaded = client.get(
        f"/api/portal/assignments/{created.json()['id']}/material",
        headers=parent_headers,
    )
    assert downloaded.status_code == 200
    assert downloaded.content == oversized_pdf[:-1]


def test_reuploading_expired_identical_pdf_starts_new_lifetime(client, database):
    faculty, batch, subject, _ = _assignment_setup(database)
    headers = {"Authorization": f"Bearer {create_token(faculty)}"}
    created = client.post(
        "/api/academics/assignments", headers=headers,
        json={
            "batchId": batch.id, "subjectId": subject.id, "title": "Worksheet",
            "dueAt": (datetime.now(timezone.utc) + timedelta(days=3)).isoformat(),
            "status": "published",
        },
    )
    assert created.status_code == 201
    assignment_id = created.json()["id"]
    path = f"/api/academics/assignments/{assignment_id}/material"
    files = {"file": ("worksheet.pdf", b"%PDF-1.4\n%%EOF\n", "application/pdf")}
    assert client.post(path, headers=headers, files=files).status_code == 200
    database.get(AssignmentMaterial, assignment_id).expires_at = (
        datetime.now(timezone.utc) - timedelta(seconds=1)
    )
    database.commit()
    retried = client.post(path, headers=headers, files=files)
    assert retried.status_code == 200
    assert datetime.fromisoformat(retried.json()["expiresAt"]) > (
        datetime.now(timezone.utc) + timedelta(hours=47)
    )
