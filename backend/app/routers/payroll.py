from datetime import datetime, timedelta
from decimal import Decimal
import hashlib
import json
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import BiometricAttendanceDay, DeviceAttendanceIdentity, StaffPayroll, User
from ..payroll import calculate_payroll, month_bounds
from ..security import require_roles
from ..services import audit
from .attendance import _staff_designation

router = APIRouter(prefix="/api/payroll", tags=["payroll"])
INDIA_TZ = ZoneInfo("Asia/Kolkata")


def _bounds(month):
    try:
        return month_bounds(month)
    except ValueError as error:
        raise HTTPException(422, str(error)) from error


def _people(db, month):
    start, end, days = _bounds(month)
    today = datetime.now(INDIA_TZ).date()
    identities = db.query(DeviceAttendanceIdentity, User).outerjoin(
        User, User.id == DeviceAttendanceIdentity.staff_user_id,
    ).filter(
        DeviceAttendanceIdentity.student_id.is_(None),
        DeviceAttendanceIdentity.is_ignored.is_(False),
    ).order_by(DeviceAttendanceIdentity.id).all()
    people, device_keys = {}, {}
    for identity, user in identities:
        if not identity.is_staff_device and not identity.staff_user_id:
            continue
        if user and user.is_test_account:
            continue
        name = user.full_name if user else identity.device_name or f"Device {identity.device_user_id}"
        if _staff_designation(name) == "Director" or (user and user.role in {"owner", "director"}):
            continue
        key = f"user:{user.id}" if user else f"identity:{identity.id}"
        person = people.setdefault(key, {
            "personKey": key, "fullName": name,
            "designation": (user.role.replace("_", " ").title() if user else "Staff"),
            "deviceIds": [], "presentDates": set(),
        })
        person["deviceIds"].append(identity.device_user_id)
        device_keys[(identity.device_key, identity.device_user_id)] = key
    # Never reuse the attendance screen's 500-row display limit for payroll.
    punches = db.query(BiometricAttendanceDay).filter(
        BiometricAttendanceDay.student_id.is_(None),
        BiometricAttendanceDay.attendance_date.between(start, min(end, today)),
    ).all()
    for punch in punches:
        key = device_keys.get((punch.device_key, punch.device_user_id))
        if key:
            people[key]["presentDates"].add(punch.attendance_date.isoformat())
    elapsed = [start + timedelta(days=index) for index in range(days) if start + timedelta(days=index) < today]
    for person in people.values():
        person["presentDates"] = sorted(person["presentDates"])
        person["deviceIds"] = sorted(set(person["deviceIds"]))
        person["unrecordedDates"] = [day.isoformat() for day in elapsed if day.isoformat() not in person["presentDates"]]
        person["presentDays"] = len(person["presentDates"])
        person["unrecordedDays"] = len(person["unrecordedDates"])
        person["attendanceFingerprint"] = hashlib.sha256(json.dumps(
            [month, person["personKey"], person["presentDates"]], separators=(",", ":"),
        ).encode()).hexdigest()
    return people


def _serialize(person, row, month, salary=None):
    result = {**person, "month": month, "id": row.id if row else None,
              "status": row.status if row else "not_prepared", "version": row.version if row else 0,
              "notes": row.notes if row else "", "salarySuggestion": str(salary) if salary is not None else None,
              "attendanceChanged": bool(row and row.attendance_fingerprint != person["attendanceFingerprint"]),
              "calculation": None}
    if row:
        result["calculation"] = (row.snapshot["calculation"] if row.status == "finalized" else
                                 calculate_payroll(month, row.monthly_salary, row.absent_days, row.advance_given))
        result["savedAttendance"] = row.snapshot.get("attendance")
    return result


@router.get("/bootstrap")
def bootstrap(month: str = Query(...), db: Session = Depends(get_db), actor: User = Depends(require_roles())):
    _, end, days = _bounds(month)
    people = _people(db, month)
    entries = {row.person_key: row for row in db.query(StaffPayroll).filter_by(month=month).all()}
    prior = {}
    for row in db.query(StaffPayroll).filter(StaffPayroll.month < month).order_by(StaffPayroll.month.desc()).all():
        prior.setdefault(row.person_key, row.monthly_salary)
    rows = [_serialize(person, entries.get(key), month, prior.get(key)) for key, person in people.items()]
    rows.sort(key=lambda row: row["fullName"].casefold())
    return {
        "month": month, "daysInMonth": days,
        "canFinalizeMonth": end < datetime.now(INDIA_TZ).date(),
        "rows": rows,
        "summary": {
            "staffCount": len(rows), "finalizedCount": sum(row["status"] == "finalized" for row in rows),
            "reviewCount": sum(row["status"] == "not_prepared" or row["attendanceChanged"] for row in rows),
            "netPayable": str(sum((Decimal(row["calculation"]["netPayable"]) for row in rows if row["calculation"]), Decimal(0))),
        },
    }


class PayrollSave(BaseModel):
    model_config = ConfigDict(extra="forbid")
    monthlySalary: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    advanceGiven: Decimal = Field(default=Decimal(0), ge=0, max_digits=14, decimal_places=2)
    absentDays: int = Field(ge=0, le=31, strict=True)
    attendanceFingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")
    version: int = Field(ge=0, strict=True)
    notes: str = Field(default="", max_length=1000)
    attendanceConfirmed: bool = False
    finalize: bool = False


@router.put("/{month}/staff/{person_key}")
def save_payroll(month: str, person_key: str, payload: PayrollSave, db: Session = Depends(get_db), actor: User = Depends(require_roles())):
    _, end, _ = _bounds(month)
    person = _people(db, month).get(person_key)
    if not person:
        raise HTTPException(404, "Staff attendance identity not found")
    if payload.attendanceFingerprint != person["attendanceFingerprint"]:
        raise HTTPException(409, "Attendance changed. Refresh payroll and review it before saving.")
    if payload.absentDays > person["unrecordedDays"]:
        raise HTTPException(422, "Absent days cannot include recorded present days, today or future days")
    if payload.finalize and (end >= datetime.now(INDIA_TZ).date() or not payload.attendanceConfirmed):
        raise HTTPException(422, "Finalize only after the month ends and the absence total has been confirmed")
    row = db.query(StaffPayroll).filter_by(month=month, person_key=person_key).with_for_update().one_or_none()
    if (row.version if row else 0) != payload.version:
        raise HTTPException(409, "Payroll was changed by another user. Refresh before saving.")
    if row and row.status == "finalized":
        raise HTTPException(409, "Reopen this payroll before changing a finalized calculation")
    before = {"status": row.status, "version": row.version} if row else None
    if row is None:
        row = StaffPayroll(person_key=person_key, month=month, version=0)
        db.add(row)
    row.monthly_salary = payload.monthlySalary
    row.advance_given = payload.advanceGiven
    row.absent_days = payload.absentDays
    row.attendance_fingerprint = person["attendanceFingerprint"]
    row.notes = payload.notes.strip()
    row.version += 1
    row.status = "finalized" if payload.finalize else "draft"
    row.updated_by = actor.id
    row.snapshot = {
        "fullName": person["fullName"], "attendance": person,
        "calculation": calculate_payroll(month, payload.monthlySalary, payload.absentDays, payload.advanceGiven),
        "attendanceConfirmed": payload.attendanceConfirmed,
    }
    try:
        db.flush()
        # Keep sensitive amounts out of shared activity summaries.
        audit(db, actor, "payroll.finalize" if payload.finalize else "payroll.save", "payroll", row.id,
              before=before, after={"month": month, "status": row.status, "version": row.version})
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "Payroll was saved elsewhere. Refresh before retrying.") from error
    return _serialize(person, row, month)


class ReopenPayroll(BaseModel):
    reason: str = Field(min_length=3, max_length=1000)
    version: int = Field(ge=1)


@router.post("/{payroll_id}/reopen")
def reopen_payroll(payroll_id: str, payload: ReopenPayroll, db: Session = Depends(get_db), actor: User = Depends(require_roles())):
    row = db.query(StaffPayroll).filter_by(id=payroll_id).with_for_update().one_or_none()
    if not row:
        raise HTTPException(404, "Payroll not found")
    if row.version != payload.version or row.status != "finalized":
        raise HTTPException(409, "Payroll changed. Refresh before reopening.")
    if len(payload.reason.strip()) < 3:
        raise HTTPException(422, "Give a reason for reopening payroll")
    row.status = "draft"
    row.version += 1
    row.updated_by = actor.id
    audit(db, actor, "payroll.reopen", "payroll", row.id,
          after={"month": row.month, "reason": payload.reason.strip(), "version": row.version})
    db.commit()
    return {"id": row.id, "status": row.status, "version": row.version}
