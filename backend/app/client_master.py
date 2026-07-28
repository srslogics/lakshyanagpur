from __future__ import annotations

from sqlalchemy.orm import Session

from .models import (
    Batch,
    FacultyTeachingAssignment,
    InventoryItem,
    Subject,
    User,
)


CLIENT_SOURCE = "Client confirmation · 28 Jul 2026"

FACULTIES = (
    {
        "name": "Meet Sir",
        "subject": "Physics",
        "subject_code": "PHY",
        "scopes": (("Tatva", "JEE"), ("Tatva", "NEET")),
    },
    {
        "name": "Kajal Ma'am",
        "subject": "Physics",
        "subject_code": "PHY",
        "scopes": (
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    },
    {
        "name": "Jitendra Sir",
        "subject": "Chemistry",
        "subject_code": "CHEM",
        "scopes": (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    },
    {
        "name": "Anita Ma'am",
        "subject": "Maths",
        "subject_code": "MATH",
        "scopes": (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    },
    {
        "name": "Kanchan Ma'am",
        "subject": "Biology",
        "subject_code": "BIO",
        "scopes": (
            ("Tatva", "JEE"),
            ("Tatva", "NEET"),
            ("Essential", "MHT-CET"),
            ("Essential", "Boards 11th & 12th Tuition"),
        ),
    },
)

INVENTORY_ITEMS = (
    ("ESS-MATH-B1", "Essential Math Booklet 1", "book"),
    ("ESS-CHEM-B1", "Essential Chemistry Booklet 1", "book"),
    ("ESS-PHYS-B1", "Essential Physics Booklet 1", "book"),
    ("ESS-BIO-B1", "Essential Biology Booklet 1", "book"),
    ("BAG-GENERIC", "Bag", "bag"),
    ("TSHIRT-GENERIC", "T-shirt", "apparel"),
)


def sync_client_master_data(db: Session) -> dict:
    """Add missing client-approved records without overwriting later owner edits."""
    created = {"faculty": 0, "subjects": 0, "assignments": 0, "inventory": 0}

    inventory_by_sku = {
        row.sku: row for row in db.query(InventoryItem).all()
    }
    for sku, name, category in INVENTORY_ITEMS:
        if sku in inventory_by_sku:
            continue
        row = InventoryItem(
            sku=sku,
            name=name,
            category=category,
            unit="piece",
            quantity_on_hand=None,
            notes="Quantity and variants have not been supplied by the client.",
            source_note=CLIENT_SOURCE,
            created_by=None,
        )
        db.add(row)
        inventory_by_sku[sku] = row
        created["inventory"] += 1

    faculties_by_name = {
        row.full_name: row
        for row in db.query(User).filter(User.role == "faculty").all()
    }
    subjects_by_code = {
        row.code: row for row in db.query(Subject).all()
    }
    batches_by_scope = {
        (row.name, row.program): row for row in db.query(Batch).all()
    }
    assignment_keys = {
        (row.faculty_id, row.batch_id, row.subject_id)
        for row in db.query(FacultyTeachingAssignment).all()
    }
    for definition in FACULTIES:
        faculty = faculties_by_name.get(definition["name"])
        if not faculty:
            faculty = User(
                full_name=definition["name"],
                mobile=None,
                email=None,
                password_hash="unprovisioned",
                role="faculty",
                is_active=True,
            )
            db.add(faculty)
            db.flush()
            faculties_by_name[faculty.full_name] = faculty
            created["faculty"] += 1

        subject = subjects_by_code.get(definition["subject_code"])
        if not subject:
            subject = Subject(
                name=definition["subject"],
                code=definition["subject_code"],
                program="All programs",
                is_active=True,
            )
            db.add(subject)
            db.flush()
            subjects_by_code[subject.code] = subject
            created["subjects"] += 1

        for batch_name, program in definition["scopes"]:
            batch = batches_by_scope.get((batch_name, program))
            if not batch:
                continue
            key = (faculty.id, batch.id, subject.id)
            if key in assignment_keys:
                continue
            db.add(FacultyTeachingAssignment(
                faculty_id=faculty.id,
                batch_id=batch.id,
                subject_id=subject.id,
                is_active=True,
                created_by=None,
            ))
            assignment_keys.add(key)
            created["assignments"] += 1

    db.commit()
    return created
