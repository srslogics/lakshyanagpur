"""Read-only academic and announcement workbooks; never include attachment bytes."""

from .models import (
    Assignment, AssignmentDownload, AssignmentMaterial, AssignmentRecipient,
    Batch, Notice, Student, StudentAcademicProfile, StudentSubjectSelection,
    Subject, User,
)
from .services import SubjectRosterResolver


def academic_sheets(db):
    profiles = (
        db.query(Student, StudentAcademicProfile)
        .outerjoin(StudentAcademicProfile, StudentAcademicProfile.student_id == Student.id)
        .filter(Student.is_test_account.is_(False))
        .order_by(Student.full_name, Student.id).all()
    )
    subjects = (
        db.query(Student, StudentSubjectSelection)
        .join(StudentSubjectSelection, StudentSubjectSelection.student_id == Student.id)
        .filter(Student.is_test_account.is_(False))
        .order_by(Student.full_name, StudentSubjectSelection.subject_name).all()
    )
    return [
        ("Academic profiles", ["Admission number", "Student", "Status", "Student code", "Batch", "Stream", "Mentor", "School", "Profile available"], [
            (s.admission_number, s.full_name, s.status, p.source_student_code if p else None,
             p.batch_name if p else None, p.source_stream if p else None,
             p.mentor_name if p else None, (p.source_school_name if p else None) or s.previous_school,
             "Yes" if p else "No")
            for s, p in profiles
        ], "Current academic profiles, including inactive students. Missing profiles and selections are not inferred. Current enrolment is in the Student register."),
        ("Subject selections", ["Admission number", "Student", "Status", "Subject", "Source selection"], [
            (s.admission_number, s.full_name, s.status, selection.subject_name, selection.source_value)
            for s, selection in subjects
        ], "Recorded subject selections only. No selection row does not mean the student has no eligible subjects."),
    ]


def assignment_sheets(db, start, end, in_range, scope):
    assignments = (
        db.query(Assignment, Batch, Subject, User)
        .join(Batch, Batch.id == Assignment.batch_id)
        .join(Subject, Subject.id == Assignment.subject_id)
        .join(User, User.id == Assignment.created_by)
        .filter(User.is_test_account.is_(False))
        .order_by(Assignment.due_at, Assignment.id).all()
    )
    assignments = [row for row in assignments if in_range(row[0].due_at, start, end)]
    ids = [row[0].id for row in assignments]
    roster = SubjectRosterResolver(db)
    progress = {(r.assignment_id, r.student_id): r for r in db.query(AssignmentRecipient).filter(AssignmentRecipient.assignment_id.in_(ids)).all()}
    downloads = {(r.assignment_id, r.student_id): r for r in db.query(AssignmentDownload).filter(AssignmentDownload.assignment_id.in_(ids)).all()}
    materials = {r.assignment_id: r for r in db.query(AssignmentMaterial).filter(AssignmentMaterial.assignment_id.in_(ids)).all()}
    # Preserve historical activity even if the student is no longer in the current roster.
    history_ids = {key[1] for key in progress.keys() | downloads.keys()}
    historical_students = {s.id: s for s in db.query(Student).filter(Student.id.in_(history_ids), Student.is_test_account.is_(False)).all()}
    summaries, details, attachments = [], [], []
    for assignment, batch, subject, author in assignments:
        eligible = {s.id: s for s in roster.students_for(batch, subject)}
        included = dict(eligible)
        for assignment_id, student_id in progress.keys() | downloads.keys():
            if assignment_id == assignment.id and student_id in historical_students:
                included[student_id] = historical_students[student_id]
        completed = sum(bool(progress.get((assignment.id, sid)) and progress[(assignment.id, sid)].status == "completed") for sid in eligible)
        summaries.append((assignment.id, assignment.title, batch.name, batch.program, subject.name,
                          author.full_name, assignment.created_at, assignment.due_at, assignment.status,
                          len(eligible), completed, assignment.instructions, assignment.external_url))
        for student in sorted(included.values(), key=lambda s: (s.full_name.casefold(), s.id)):
            entry = progress.get((assignment.id, student.id))
            download = downloads.get((assignment.id, student.id))
            details.append((assignment.id, assignment.title, student.admission_number, student.full_name,
                            "Yes" if student.id in eligible else "No", entry.status if entry else "not_started",
                            entry.updated_at if entry else None, download.first_downloaded_at if download else None,
                            download.last_downloaded_at if download else None, download.download_count if download else 0))
        material = materials.get(assignment.id)
        if material:
            attachments.append((assignment.id, assignment.title, material.filename, material.size_bytes,
                                material.created_at, material.expires_at))
    return [
        ("Assignments", ["Assignment ID", "Title", "Batch", "Program", "Subject", "Published by", "Created (IST)", "Due (IST)", "Status", "Current recipients", "Completed recipients", "Instructions", "External link"], summaries, scope + " Filtered by due date. Recipient counts use the current subject roster."),
        ("Student progress", ["Assignment ID", "Assignment", "Admission number", "Student", "Currently eligible", "Progress", "Updated (IST)", "First PDF download (IST)", "Last PDF download (IST)", "PDF download count"], details, "Current eligible students plus historical progress/downloads. Missing progress is not started; downloading a PDF does not prove completion."),
        ("Material details", ["Assignment ID", "Assignment", "PDF filename", "Size (bytes)", "Uploaded (IST)", "Expires (IST)"], attachments, "Metadata for attachments still stored in the application. Expired or deleted files may be absent. PDF contents are not embedded in this workbook."),
    ]


def announcement_sheets(db, start, end, in_range, scope):
    notices = (
        db.query(Notice, User, Batch, Subject)
        .join(User, User.id == Notice.created_by)
        .outerjoin(Batch, Batch.id == Notice.batch_id)
        .outerjoin(Subject, Subject.id == Notice.subject_id)
        .filter(User.is_test_account.is_(False))
        .order_by(Notice.created_at, Notice.id).all()
    )
    return [("Announcements", ["Notice ID", "Title", "Message", "Audience", "Batch", "Subject", "Channel", "Status", "Author", "Created (IST)", "Published (IST)"], [
        (n.id, n.title, n.body, n.audience, b.name if b else None, s.name if s else None,
         n.channel, n.status, u.full_name, n.created_at, n.published_at)
        for n, u, b, s in notices if in_range(n.created_at, start, end)
    ], scope + " Filtered by creation date, including unpublished notices. Publication is not proof of delivery or reading. Private conversations and device subscription credentials are excluded.")]
