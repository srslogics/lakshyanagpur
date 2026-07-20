from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Assignment, AttendanceEntry, AuditLog, ClassSession, Lead, Notice, PaymentTransaction, Student, User
from ..security import require_roles

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/overview")
def overview(db: Session = Depends(get_db), user: User = Depends(require_roles("owner"))):
    now = datetime.now(timezone.utc)
    lead_rows = db.query(Lead.stage, func.count(Lead.id)).group_by(Lead.stage).all()
    attendance_rows = db.query(AttendanceEntry.status, func.count()).group_by(AttendanceEntry.status).all()
    attendance = {status: count for status, count in attendance_rows}
    attendance_total = sum(attendance.values())
    paid = db.query(func.coalesce(func.sum(PaymentTransaction.amount), 0)).filter(PaymentTransaction.transaction_type == "payment").scalar() or 0
    recent = db.query(AuditLog, User).outerjoin(User, User.id == AuditLog.actor_id).order_by(AuditLog.created_at.desc()).limit(10).all()
    return {
        "metrics": {
            "students": db.query(Student).count(),
            "activeUsers": db.query(User).filter(User.is_active.is_(True)).count(),
            "scheduledClasses": db.query(ClassSession).filter(ClassSession.starts_at >= now).count(),
            "publishedNotices": db.query(Notice).filter_by(status="published").count(),
            "assignments": db.query(Assignment).count(),
            "overdueAssignments": db.query(Assignment).filter(Assignment.status == "published", Assignment.due_at < now).count(),
            "recordedPayments": paid,
            "attendanceRate": round(((attendance_total - attendance.get("absent", 0)) / attendance_total * 100), 1) if attendance_total else None,
        },
        "leadFunnel": [{"stage": stage, "count": count} for stage, count in lead_rows],
        "attendance": [{"status": status, "count": count} for status, count in attendance_rows],
        "recentAudit": [{"id": log.id, "action": log.action, "entityType": log.entity_type, "actor": actor.full_name if actor else "System", "createdAt": log.created_at} for log, actor in recent],
    }
