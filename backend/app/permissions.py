from __future__ import annotations

from fastapi import Request
from sqlalchemy.orm import Session

from .models import User, UserModulePermission


MODULES = (
    "admissions",
    "students",
    "finance",
    "attendance",
    "academics",
    "examinations",
    "timetable",
    "communication",
    "inventory",
    "reports",
)

MODULE_LABELS = {
    "admissions": "Admissions",
    "students": "Students",
    "finance": "Fees & finance",
    "attendance": "Attendance",
    "academics": "Academics",
    "examinations": "Examinations",
    "timetable": "Faculty & timetable",
    "communication": "Communication",
    "inventory": "Inventory",
    "reports": "Reports",
}

_FULL = {"read": True, "create": True, "edit": True}
_READ = {"read": True, "create": False, "edit": False}
_NONE = {"read": False, "create": False, "edit": False}

ROLE_DEFAULTS = {
    "admissions_manager": {
        "admissions": _FULL,
        "students": _READ,
        "finance": _FULL,
        "communication": _FULL,
    },
    "counsellor": {"admissions": _FULL},
    "front_desk": {
        "admissions": _FULL,
        "students": _READ,
        "timetable": _READ,
        "communication": _FULL,
    },
    "accounts": {
        "students": _READ,
        "finance": _FULL,
        "inventory": _READ,
        "reports": _READ,
    },
    "academic_coordinator": {
        "students": _READ,
        "attendance": _FULL,
        "academics": _FULL,
        "examinations": _FULL,
        "timetable": _FULL,
        "communication": _FULL,
        "reports": _READ,
    },
    "faculty": {
        "academics": _FULL,
        "examinations": _FULL,
        "timetable": _READ,
    },
    "storekeeper": {"inventory": _FULL},
}

PATH_MODULES = {
    "/api/admissions": "admissions",
    "/api/students": "students",
    "/api/finance": "finance",
    "/api/attendance": "attendance",
    "/api/academics": "academics",
    "/api/examinations": "examinations",
    "/api/timetable": "timetable",
    "/api/communication": "communication",
    "/api/inventory": "inventory",
    "/api/reports": "reports",
}

CREATE_ROUTES = {
    "/api/admissions/leads",
    "/api/students",
    "/api/finance/agreements",
    "/api/finance/payments",
    "/api/finance/installments",
    "/api/attendance/manual-registers",
    "/api/academics/assignments",
    "/api/examinations",
    "/api/timetable/teaching-assignments",
    "/api/timetable/sessions",
    "/api/communication/threads",
    "/api/communication/threads/{thread_id}/messages",
    "/api/communication/notices",
    "/api/inventory/items",
    "/api/inventory/items/{item_id}/movements",
}


def role_default_permissions(role: str) -> dict[str, dict[str, bool]]:
    if role == "owner":
        return {module: dict(_FULL) for module in MODULES}
    defaults = ROLE_DEFAULTS.get(role, {})
    return {module: dict(defaults.get(module, _NONE)) for module in MODULES}


def permission_rows(db: Session, user_id: str) -> dict[str, UserModulePermission]:
    return {
        row.module: row
        for row in db.query(UserModulePermission).filter(UserModulePermission.user_id == user_id).all()
    }


def permissions_from_rows(
    user: User,
    rows: dict[str, UserModulePermission],
) -> dict[str, dict[str, bool]]:
    permissions = role_default_permissions(user.role)
    if user.role == "owner":
        return permissions
    for module, row in rows.items():
        if module in permissions:
            permissions[module] = {
                "read": row.can_read,
                "create": row.can_create,
                "edit": row.can_edit,
            }
    return permissions


def effective_permissions(db: Session, user: User) -> dict[str, dict[str, bool]]:
    if user.role == "owner":
        return role_default_permissions(user.role)
    return permissions_from_rows(user, permission_rows(db, user.id))


def module_for_request(request: Request) -> str | None:
    path = request.url.path
    return next((module for prefix, module in PATH_MODULES.items() if path.startswith(prefix)), None)


def action_for_request(request: Request) -> str:
    if request.method in {"GET", "HEAD", "OPTIONS"}:
        return "read"
    if request.method == "POST":
        route = request.scope.get("route")
        route_path = getattr(route, "path", request.url.path)
        return "create" if route_path in CREATE_ROUTES else "edit"
    return "edit"


def explicit_permission(db: Session, user_id: str, module: str, action: str) -> bool | None:
    row = (
        db.query(UserModulePermission)
        .filter(UserModulePermission.user_id == user_id, UserModulePermission.module == module)
        .one_or_none()
    )
    if row is None:
        return None
    return bool(getattr(row, f"can_{action}"))


def has_permission(db: Session, user: User, module: str, action: str = "read") -> bool:
    if user.role == "owner":
        return True
    override = explicit_permission(db, user.id, module, action)
    if override is not None:
        return override
    return role_default_permissions(user.role).get(module, _NONE).get(action, False)
