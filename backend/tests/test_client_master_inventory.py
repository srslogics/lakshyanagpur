import json
from pathlib import Path

from app.client_master import sync_client_master_data
from app.importers.academic_workbook import import_manifest as import_academics
from app.importers.legacy_admissions import import_manifest as import_admissions
from app.models import (
    Batch,
    FacultyTeachingAssignment,
    InventoryItem,
    Student,
    Subject,
    User,
)


DATA_DIR = Path(__file__).parents[1] / "data" / "imports"


def _manifest(name):
    return json.loads((DATA_DIR / name).read_text())


def test_client_faculty_allocations_match_confirmed_scopes(database):
    import_admissions(database, _manifest("admission_2026_27.json"))
    import_academics(database, _manifest("demo_attendance_2026.json"))

    faculties = database.query(User).filter_by(role="faculty").all()
    assert {row.full_name for row in faculties} == {
        "Meet Sir",
        "Jitendra Sir",
        "Anita Ma'am",
        "Kanchan Ma'am",
        "Kajal Ma'am",
    }
    assert {row.full_name: row.mobile for row in faculties} == {
        "Meet Sir": "9325511100",
        "Jitendra Sir": "9850242456",
        "Anita Ma'am": "9923057717",
        "Kanchan Ma'am": "9049834525",
        "Kajal Ma'am": "9156376488",
    }
    assert all(row.password_hash == "unprovisioned" for row in faculties)

    counts = {
        faculty.full_name: (
            database.query(FacultyTeachingAssignment)
            .filter_by(faculty_id=faculty.id, is_active=True)
            .count()
        )
        for faculty in faculties
    }
    assert counts == {
        "Meet Sir": 2,
        "Kajal Ma'am": 2,
        "Jitendra Sir": 4,
        "Anita Ma'am": 4,
        "Kanchan Ma'am": 4,
    }

    meet = next(row for row in faculties if row.full_name == "Meet Sir")
    meet_scopes = {
        (batch.name, batch.program, subject.name)
        for _, batch, subject in (
            database.query(FacultyTeachingAssignment, Batch, Subject)
            .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
            .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
            .filter(FacultyTeachingAssignment.faculty_id == meet.id)
            .all()
        )
    }
    assert meet_scopes == {
        ("Tatva", "JEE", "Physics"),
        ("Tatva", "NEET", "Physics"),
    }

    kajal = next(row for row in faculties if row.full_name == "Kajal Ma'am")
    kajal_scopes = {
        (batch.name, batch.program, subject.name)
        for _, batch, subject in (
            database.query(FacultyTeachingAssignment, Batch, Subject)
            .join(Batch, Batch.id == FacultyTeachingAssignment.batch_id)
            .join(Subject, Subject.id == FacultyTeachingAssignment.subject_id)
            .filter(FacultyTeachingAssignment.faculty_id == kajal.id)
            .all()
        )
    }
    assert kajal_scopes == {
        ("Essential", "MHT-CET", "Physics"),
        ("Essential", "Boards 11th & 12th Tuition", "Physics"),
    }


def test_client_inventory_is_idempotent_and_quantities_remain_unknown(database):
    first = sync_client_master_data(database)
    second = sync_client_master_data(database)

    assert first["inventory"] == 6
    assert second == {
        "faculty": 0,
        "subjects": 0,
        "assignments": 0,
        "inventory": 0,
    }
    rows = database.query(InventoryItem).order_by(InventoryItem.sku).all()
    assert len(rows) == 6
    assert all(row.quantity_on_hand is None for row in rows)
    assert {row.name for row in rows} == {
        "Essential Math Booklet 1",
        "Essential Chemistry Booklet 1",
        "Essential Physics Booklet 1",
        "Essential Biology Booklet 1",
        "Bag",
        "T-shirt",
    }


def test_owner_can_record_inventory_quantity_without_changing_source_name(
    client,
    database,
    owner_headers,
):
    sync_client_master_data(database)
    bootstrap = client.get("/api/inventory/bootstrap", headers=owner_headers)
    assert bootstrap.status_code == 200
    assert bootstrap.json()["summary"] == {
        "activeItems": 6,
        "knownQuantities": 0,
        "quantityPending": 6,
        "lowStock": 0,
        "categories": 3,
        "issuedToStudents": 0,
        "studentsWithItems": 0,
    }
    item = next(
        row for row in bootstrap.json()["items"]
        if row["sku"] == "ESS-PHYS-B1"
    )
    updated = client.patch(
        f"/api/inventory/items/{item['id']}",
        headers=owner_headers,
        json={
            "name": item["name"],
            "category": item["category"],
            "unit": "booklet",
            "quantityOnHand": 25,
            "notes": "Count verified by owner.",
            "isActive": True,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["quantityOnHand"] == 25
    assert updated.json()["sku"] == "ESS-PHYS-B1"
    movements = client.get(
        f"/api/inventory/movements?item_id={item['id']}",
        headers=owner_headers,
    )
    assert movements.status_code == 200
    assert movements.json()[0]["movementType"] == "opening"
    assert movements.json()[0]["balanceAfter"] == 25


def test_inventory_issue_return_and_negative_stock_control(
    client,
    database,
    owner_headers,
):
    sync_client_master_data(database)
    item = client.get(
        "/api/inventory/bootstrap",
        headers=owner_headers,
    ).json()["items"][0]
    opened = client.patch(
        f"/api/inventory/items/{item['id']}",
        headers=owner_headers,
        json={
            "name": item["name"],
            "category": item["category"],
            "unit": item["unit"],
            "quantityOnHand": 10,
            "reorderLevel": 2,
            "vendorReference": "Local supplier",
            "notes": "Opening count",
            "isActive": True,
        },
    )
    assert opened.status_code == 200
    issue = client.post(
        f"/api/inventory/items/{item['id']}/movements",
        headers=owner_headers,
        json={
            "movementType": "issue",
            "quantity": 3,
            "occurredOn": "2026-07-29",
            "targetType": "batch",
            "targetReference": "Essential",
            "reference": "ISS-001",
            "reason": "Issued for classroom distribution",
        },
    )
    assert issue.status_code == 201
    assert issue.json()["quantityDelta"] == -3
    assert issue.json()["balanceAfter"] == 7
    blocked = client.post(
        f"/api/inventory/items/{item['id']}/movements",
        headers=owner_headers,
        json={
            "movementType": "issue",
            "quantity": 8,
            "occurredOn": "2026-07-29",
            "targetType": "batch",
            "targetReference": "Tatva",
            "reason": "Should be blocked",
        },
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["code"] == "INSUFFICIENT_STOCK"


def test_student_inventory_register_updates_stock_and_blocks_excess_return(
    client,
    database,
    owner_headers,
):
    sync_client_master_data(database)
    student = Student(
        admission_number="LI-2026-00999",
        full_name="Inventory Student",
        mobile="9000000998",
        status="active",
        data_quality_status="ready",
    )
    database.add(student)
    database.commit()
    item = next(
        row
        for row in client.get(
            "/api/inventory/bootstrap",
            headers=owner_headers,
        ).json()["items"]
        if row["sku"] == "ESS-MATH-B1"
    )
    opened = client.patch(
        f"/api/inventory/items/{item['id']}",
        headers=owner_headers,
        json={
            "name": item["name"],
            "category": item["category"],
            "unit": "booklet",
            "quantityOnHand": 10,
            "reorderLevel": 2,
            "notes": "Opening count",
            "isActive": True,
        },
    )
    assert opened.status_code == 200
    issued = client.post(
        f"/api/inventory/items/{item['id']}/movements",
        headers=owner_headers,
        json={
            "movementType": "issue",
            "quantity": 2,
            "occurredOn": "2026-08-03",
            "targetType": "student",
            "studentId": student.id,
            "reference": "KIT-001",
            "reason": "Issued from the student profile",
        },
    )
    assert issued.status_code == 201
    assert issued.json()["balanceAfter"] == 8

    register = client.get(
        f"/api/inventory/students/{student.id}",
        headers=owner_headers,
    )
    assert register.status_code == 200
    assert register.json()["summary"] == {
        "itemTypes": 1,
        "issuedUnits": 2,
        "transactions": 1,
    }
    assert register.json()["holdings"] == [{
        "itemId": item["id"],
        "itemName": item["name"],
        "sku": item["sku"],
        "category": "book",
        "unit": "booklet",
        "quantityIssued": 2,
        "lastIssuedOn": "2026-08-03",
    }]
    inventory = client.get(
        "/api/inventory/bootstrap",
        headers=owner_headers,
    ).json()
    assert inventory["summary"]["issuedToStudents"] == 2
    assert inventory["summary"]["studentsWithItems"] == 1

    returned = client.post(
        f"/api/inventory/items/{item['id']}/movements",
        headers=owner_headers,
        json={
            "movementType": "return",
            "quantity": 1,
            "occurredOn": "2026-08-04",
            "targetType": "student",
            "studentId": student.id,
            "reason": "One booklet returned",
        },
    )
    assert returned.status_code == 201
    assert returned.json()["balanceAfter"] == 9
    assert client.get(
        f"/api/inventory/students/{student.id}",
        headers=owner_headers,
    ).json()["holdings"][0]["quantityIssued"] == 1

    blocked = client.post(
        f"/api/inventory/items/{item['id']}/movements",
        headers=owner_headers,
        json={
            "movementType": "return",
            "quantity": 2,
            "occurredOn": "2026-08-04",
            "targetType": "student",
            "studentId": student.id,
            "reason": "Return more than issued",
        },
    )
    assert blocked.status_code == 409
    assert blocked.json()["detail"]["code"] == (
        "RETURN_EXCEEDS_STUDENT_BALANCE"
    )
    unchanged = client.get(
        f"/api/inventory/students/{student.id}",
        headers=owner_headers,
    ).json()
    assert unchanged["holdings"][0]["quantityIssued"] == 1
    assert next(
        row for row in unchanged["availableItems"] if row["id"] == item["id"]
    )["quantityOnHand"] == 9


def test_non_inventory_role_cannot_read_inventory(client, parent_headers):
    assert client.get(
        "/api/inventory/bootstrap",
        headers=parent_headers,
    ).status_code == 403
