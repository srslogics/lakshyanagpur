from datetime import date, datetime, timezone
from decimal import Decimal
from types import SimpleNamespace

from app.models import (AttendanceEntry, AttendanceRegister, DeviceAttendanceIdentity,
                        InventoryItem, InventoryMovement, StaffAttendanceWorkday, StaffPayroll, User,
                        UserModulePermission)
from app.routers.payroll import _people, bootstrap
from app.routers.reports import _recorded_attendance_counts
from app.routers.auth import _login_key
from app.schemas import LoginRequest
from test_payroll import _payroll_people
from test_examinations import examination_setup


def test_payroll_mapping_keeps_saved_calculation_and_archived_history(database):
    owner, staff, _, _ = _payroll_people(database)
    identity = database.query(DeviceAttendanceIdentity).filter_by(staff_user_id=staff.id).one()
    identity.staff_user_id = None
    database.commit()
    key = f"identity:{identity.id}"
    saved = StaffPayroll(person_key=key, month="2026-08", monthly_salary=30000,
                         advance_given=0, absent_days=0, attendance_fingerprint="0"*64,
                         updated_by=owner.id, snapshot={"fullName": staff.full_name})
    database.add(saved); database.commit()
    identity.staff_user_id = staff.id; database.commit()
    row = bootstrap("2026-08", database, owner)["rows"][0]
    assert row["id"] == saved.id and row["calculation"]["netPayable"] == "30000.00"
    identity.is_ignored = True; database.commit()
    row = bootstrap("2026-08", database, owner)["rows"][0]
    assert row["archived"] is True and row["id"] == saved.id


def test_payroll_duplicate_devices_count_one_day_and_flag_conflicts(database):
    owner, staff, _, _ = _payroll_people(database)
    identity = database.query(DeviceAttendanceIdentity).filter_by(staff_user_id=staff.id).one()
    other = DeviceAttendanceIdentity(device_key="other", device_user_id="41", staff_user_id=staff.id,
                                    is_staff_device=True, created_by=owner.id)
    database.add(other)
    rows = []
    for device in (identity.device_key, "other"):
        row = StaffAttendanceWorkday(import_batch_id="fixture", device_key=device, device_user_id="41",
                                    attendance_date=date(2026,8,2), attendance_status="half_day",
                                    work_duration_minutes=240, overtime_minutes=0, punch_count=2)
        rows.append(row); database.add(row)
    database.commit()
    person = next(iter(_people(database, "2026-08").values()))
    assert person["totalWorkMinutes"] == 240
    assert person["explicitAbsentDays"] == .5
    assert person["attendanceConflicts"] == []
    rows[1].attendance_status = "absent"; database.commit()
    person = next(iter(_people(database, "2026-08").values()))
    assert person["attendanceConflicts"] == ["2026-08-02"]


def test_reports_exclude_drafts_and_deduplicate_dates(database):
    _, _, _, _, _, student, _ = examination_setup(database)
    owner = database.query(User).filter_by(role="owner").one()
    for index, status in enumerate(("draft", "submitted", "submitted")):
        reg = AttendanceRegister(status=status, register_kind="manual", attendance_date=date(2026,8,2),
                                 batch_name=f"scope-{index}", stream_name="All", subject_name="All")
        database.add(reg); database.flush()
        database.add(AttendanceEntry(register_id=reg.id, student_id=student.id,
                                     status="absent" if status == "draft" else "present", marked_by=owner.id))
    database.commit()
    assert _recorded_attendance_counts(database) == {"present": 1}


def test_parent_throttle_is_independent_but_nonparent_portals_share_account_bucket():
    request = SimpleNamespace(client=SimpleNamespace(host="test"))
    def key(portal):
        return _login_key(request, LoginRequest(mobile="9000000001", password="password", portal=portal))
    assert key("parent") != key("student")
    assert key("student") == key("operations")


def test_inventory_request_replay_and_payload_mismatch(client, database, owner_headers):
    item = InventoryItem(sku="AUDIT", name="Audit book", category="stationery", unit="unit",
                         quantity_on_hand=20, reorder_level=0)
    database.add(item); database.commit()
    headers = {**owner_headers, "Idempotency-Key": "audit-movement-request-001"}
    payload = {"movementType":"issue", "quantity":2, "occurredOn":"2026-08-02", "reason":"Audit test"}
    url = f"/api/inventory/items/{item.id}/movements"
    first = client.post(url, headers=headers, json=payload)
    assert first.status_code == 201, first.text
    retry = client.post(url, headers=headers, json=payload)
    assert retry.status_code == 201 and retry.json() == first.json()
    database.refresh(item)
    assert item.quantity_on_hand == 18 and database.query(InventoryMovement).count() == 1
    assert client.post(url, headers=headers, json={**payload, "quantity":3}).status_code == 409


def test_explicit_exam_edit_permission_is_honored(database):
    from app.routers.examinations import _can_manage
    user = database.query(User).filter_by(role="parent_student").one()
    exam = SimpleNamespace(faculty_id="someone-else")
    assert not _can_manage(user, exam, database)
    database.add(UserModulePermission(user_id=user.id, module="examinations", can_read=True, can_edit=True))
    database.commit()
    assert _can_manage(user, exam, database)


def test_postgres_lock_is_transaction_scoped_and_stable():
    from app.concurrency import transaction_lock
    calls = []
    db = SimpleNamespace(get_bind=lambda: SimpleNamespace(dialect=SimpleNamespace(name="postgresql")),
                         execute=lambda sql, params: calls.append((str(sql), params)))
    transaction_lock(db, "exam:one"); transaction_lock(db, "exam:one")
    assert calls[0] == calls[1]
    assert "pg_advisory_xact_lock" in calls[0][0]


def test_unknown_arrival_is_not_fabricated():
    from app.routers.attendance import _arrival_at
    assert _arrival_at("present", None) is None
    value = datetime(2026,8,2,5,tzinfo=timezone.utc)
    assert _arrival_at("present", value) == value
