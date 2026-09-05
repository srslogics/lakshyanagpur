from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from app.models import (
    AuditLog,
    BiometricAttendanceDay,
    BiometricImportBatch,
    DeviceAttendanceIdentity,
    StaffAttendanceWorkday,
    StaffPayroll,
    User,
)
from app.payroll import calculate_payroll, month_bounds
from app.security import create_token, hash_password


def _headers(user):
    return {"Authorization": f"Bearer {create_token(user)}"}


def _payroll_people(database):
    owner = database.query(User).filter_by(role="owner").one()
    staff = User(
        full_name="Office Staff",
        mobile="9000000041",
        role="front_desk",
        password_hash=hash_password("Password123!"),
    )
    director = User(
        full_name="Institute Director",
        mobile="9000000042",
        role="director",
        password_hash=hash_password("Password123!"),
    )
    accounts = User(
        full_name="Payroll Accounts",
        mobile="9000000043",
        role="accounts",
        password_hash=hash_password("Password123!"),
    )
    database.add_all([staff, director, accounts])
    database.flush()
    staff_identity = DeviceAttendanceIdentity(
        device_key="payroll-device",
        device_user_id="41",
        device_name="Office Staff",
        staff_user_id=staff.id,
        is_staff_device=True,
        is_ignored=False,
        created_by=owner.id,
    )
    director_identity = DeviceAttendanceIdentity(
        device_key="payroll-device",
        device_user_id="42",
        device_name="Institute Director",
        staff_user_id=director.id,
        is_staff_device=True,
        is_ignored=False,
        created_by=owner.id,
    )
    batch = BiometricImportBatch(
        device_key="payroll-device",
        source_name="august.xls",
        source_hash="a" * 64,
        source_sheet="Staff",
        rows_seen=4,
        attendance_days=2,
        matched_students=0,
        ignored_device_ids=0,
        duplicate_rows=0,
        actor_id=owner.id,
    )
    database.add_all([staff_identity, director_identity, batch])
    database.flush()
    for day in (date(2026, 8, 1), date(2026, 8, 15)):
        database.add(BiometricAttendanceDay(
            import_batch_id=batch.id,
            device_key="payroll-device",
            device_user_id="41",
            staff_user_id=staff.id,
            attendance_date=day,
            first_punch_at=datetime(day.year, day.month, day.day, 3, 0, tzinfo=timezone.utc),
            last_punch_at=datetime(day.year, day.month, day.day, 12, 0, tzinfo=timezone.utc),
        ))
    database.commit()
    return owner, staff, director, accounts


@pytest.mark.parametrize(
    ("month", "expected_days"),
    [("2026-02", 28), ("2024-02", 29), ("2026-04", 30), ("2026-08", 31)],
)
def test_payroll_uses_calendar_days_for_each_month(month, expected_days):
    assert month_bounds(month)[2] == expected_days


def test_payroll_formula_retains_precision_until_final_amount():
    result = calculate_payroll("2026-08", Decimal("10000"), 1, Decimal("500"))
    assert result == {
        "daysInMonth": 31,
        "absentDays": 1,
        "payableDays": 30,
        "monthlySalary": "10000.00",
        "perDayRate": "322.580645",
        "payableAmount": "9677.42",
        "advanceGiven": "500.00",
        "netPayable": "9177.42",
    }


def test_payroll_formula_rejects_invalid_values():
    with pytest.raises(ValueError):
        calculate_payroll("2026-02", Decimal("10000"), 29, Decimal("0"))
    with pytest.raises(ValueError):
        calculate_payroll("2026-02", Decimal("-1"), 0, Decimal("0"))
    with pytest.raises(ValueError):
        month_bounds("2026-13")


def test_payroll_bootstrap_uses_biometrics_and_excludes_directors(client, database):
    owner, staff, director, accounts = _payroll_people(database)
    response = client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(owner))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["daysInMonth"] == 31
    assert body["canFinalizeMonth"] is True
    assert body["summary"] == {
        "staffCount": 1,
        "finalizedCount": 0,
        "reviewCount": 1,
        "netPayable": "0",
    }
    assert len(body["rows"]) == 1
    row = body["rows"][0]
    assert row["fullName"] == "Office Staff"
    assert row["presentDays"] == 2
    assert row["unrecordedDays"] == 29
    assert row["presentDates"] == ["2026-08-01", "2026-08-15"]

    assert client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(director)).status_code == 200
    assert client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(accounts)).status_code == 200
    assert client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(staff)).status_code == 403

    endpoint = f"/api/payroll/2026-08/staff/{row['personKey']}"
    draft = {
        "monthlySalary": "31000.00",
        "advanceGiven": "0",
        "absentDays": 0,
        "attendanceFingerprint": row["attendanceFingerprint"],
        "version": 0,
        "attendanceConfirmed": False,
        "finalize": False,
    }
    assert client.put(endpoint, headers=_headers(accounts), json=draft).status_code == 200
    draft["version"] = 1
    assert client.put(endpoint, headers=_headers(director), json=draft).status_code == 403


def test_payroll_includes_device_work_time_and_half_day_absence_suggestion(client, database):
    owner, staff, _, _ = _payroll_people(database)
    batch = database.query(BiometricImportBatch).one()
    database.add_all([
        StaffAttendanceWorkday(
            import_batch_id=batch.id, device_key="payroll-device", device_user_id="41",
            staff_user_id=staff.id, attendance_date=date(2026, 8, 1), attendance_status="present",
            first_punch_at=datetime(2026, 8, 1, 3, 0, tzinfo=timezone.utc),
            last_punch_at=datetime(2026, 8, 1, 11, 0, tzinfo=timezone.utc),
            work_duration_minutes=480, overtime_minutes=30, punch_count=2,
        ),
        StaffAttendanceWorkday(
            import_batch_id=batch.id, device_key="payroll-device", device_user_id="41",
            staff_user_id=staff.id, attendance_date=date(2026, 8, 2), attendance_status="half_day",
            first_punch_at=datetime(2026, 8, 2, 3, 0, tzinfo=timezone.utc),
            last_punch_at=datetime(2026, 8, 2, 7, 0, tzinfo=timezone.utc),
            work_duration_minutes=240, overtime_minutes=0, punch_count=2,
        ),
        StaffAttendanceWorkday(
            import_batch_id=batch.id, device_key="payroll-device", device_user_id="41",
            staff_user_id=staff.id, attendance_date=date(2026, 8, 3), attendance_status="absent",
            work_duration_minutes=0, overtime_minutes=0, punch_count=0,
        ),
    ])
    database.commit()
    row = client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(owner)).json()["rows"][0]
    assert row["totalWorkMinutes"] == 720
    assert row["overtimeMinutes"] == 30
    assert row["averageWorkMinutes"] == 360
    assert row["explicitAbsentDays"] == 1.5
    assert row["dailyWorkLog"][2]["status"] == "absent"


def test_payroll_finalize_is_confirmed_audited_and_immutable(client, database):
    owner, _, director, _ = _payroll_people(database)
    row = client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(owner)).json()["rows"][0]
    payload = {
        "monthlySalary": "31000.00",
        "advanceGiven": "1000.00",
        "absentDays": 2,
        "attendanceFingerprint": row["attendanceFingerprint"],
        "version": 0,
        "notes": "Approved advance",
        "attendanceConfirmed": False,
        "finalize": True,
    }
    endpoint = f"/api/payroll/2026-08/staff/{row['personKey']}"
    rejected = client.put(endpoint, headers=_headers(owner), json=payload)
    assert rejected.status_code == 422

    payload["attendanceConfirmed"] = True
    finalized = client.put(endpoint, headers=_headers(owner), json=payload)
    assert finalized.status_code == 200, finalized.text
    saved = finalized.json()
    assert saved["status"] == "finalized"
    assert saved["calculation"]["payableDays"] == 29
    assert saved["calculation"]["payableAmount"] == "29000.00"
    assert saved["calculation"]["netPayable"] == "28000.00"
    assert database.query(StaffPayroll).one().version == 1
    assert database.query(AuditLog).filter_by(action="payroll.finalize").count() == 1

    payload["version"] = 1
    assert client.put(endpoint, headers=_headers(owner), json=payload).status_code == 409
    assert client.put(endpoint, headers=_headers(director), json=payload).status_code == 403

    reopened = client.post(
        f"/api/payroll/{saved['id']}/reopen",
        headers=_headers(owner),
        json={"reason": "Correct approved advance", "version": 1},
    )
    assert reopened.status_code == 200
    assert reopened.json()["version"] == 2
    assert database.query(AuditLog).filter_by(action="payroll.reopen").count() == 1


def test_payroll_rejects_unconfirmed_missing_days_and_stale_attendance(client, database):
    owner, staff, _, _ = _payroll_people(database)
    row = client.get("/api/payroll/bootstrap?month=2026-08", headers=_headers(owner)).json()["rows"][0]
    endpoint = f"/api/payroll/2026-08/staff/{row['personKey']}"
    too_many_absences = {
        "monthlySalary": "31000.00",
        "advanceGiven": "0",
        "absentDays": 30,
        "attendanceFingerprint": row["attendanceFingerprint"],
        "version": 0,
        "attendanceConfirmed": False,
        "finalize": False,
    }
    assert client.put(endpoint, headers=_headers(owner), json=too_many_absences).status_code == 422

    batch = database.query(BiometricImportBatch).one()
    database.add(BiometricAttendanceDay(
        import_batch_id=batch.id,
        device_key="payroll-device",
        device_user_id="41",
        staff_user_id=staff.id,
        attendance_date=date(2026, 8, 20),
        first_punch_at=datetime(2026, 8, 20, 3, 0, tzinfo=timezone.utc),
    ))
    database.commit()
    too_many_absences["absentDays"] = 0
    assert client.put(endpoint, headers=_headers(owner), json=too_many_absences).status_code == 409
