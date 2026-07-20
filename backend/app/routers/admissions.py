from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Lead, LeadActivity, User
from ..schemas import ConversionRequest, ConversionResult, LEAD_STAGES, LeadActivityUpdate, LeadCreate, LeadRead, LeadStageUpdate, Page
from ..security import require_roles
from ..services import audit, convert_lead

WRITE_ROLES = ("owner", "admissions_manager", "counsellor", "front_desk")
router = APIRouter(prefix="/api/admissions", tags=["admissions"])


@router.get("/bootstrap")
def bootstrap(user: User = Depends(require_roles(*WRITE_ROLES))):
    return {"stageOrder": list(LEAD_STAGES), "sources": ["walk-in", "website", "phone", "whatsapp", "referral", "campaign", "seminar", "social media"]}


@router.get("/leads", response_model=Page)
def list_leads(search: str | None = None, stage: str | None = None, counsellor: str | None = None, page: int = Query(1, ge=1), page_size: int = Query(25, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(require_roles(*WRITE_ROLES))):
    query = db.query(Lead)
    if search:
        term = f"%{search.strip()}%"; query = query.filter(or_(Lead.student.ilike(term), Lead.mobile.ilike(term), Lead.parent.ilike(term), Lead.program.ilike(term)))
    if stage: query = query.filter(Lead.stage == stage)
    if counsellor: query = query.filter(Lead.counsellor == counsellor)
    if user.role == "counsellor": query = query.filter(Lead.owner_id == user.id)
    total = query.count(); items = query.order_by(Lead.next_follow_up_at.asc().nullslast(), Lead.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "pageSize": page_size}


@router.post("/leads", response_model=LeadRead, status_code=201)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db), user: User = Depends(require_roles(*WRITE_ROLES))):
    duplicate = db.query(Lead).filter(Lead.mobile == payload.mobile, Lead.stage.notin_(("Lost", "Not Interested", "Converted"))).first()
    if duplicate: raise HTTPException(409, detail={"code": "DUPLICATE_MOBILE", "message": "An active lead already uses this mobile number", "leadId": duplicate.id})
    lead = Lead(**payload.model_dump(by_alias=False), owner_id=user.id if user.role == "counsellor" else None)
    db.add(lead); db.flush(); audit(db, user, "admissions.lead.create", "lead", lead.id, after={"stage": lead.stage, "mobile": lead.mobile}); db.commit(); db.refresh(lead)
    return lead


@router.patch("/leads/{lead_id}/stage", response_model=LeadRead)
def update_stage(lead_id: str, payload: LeadStageUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(*WRITE_ROLES))):
    lead = db.get(Lead, lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    if payload.stage == "Converted": raise HTTPException(409, "Use the conversion endpoint so downstream records are created")
    before = lead.stage; lead.stage = payload.stage; audit(db, user, "admissions.stage.change", "lead", lead.id, {"stage": before}, {"stage": lead.stage}); db.commit(); db.refresh(lead)
    return lead


@router.post("/leads/{lead_id}/activity", response_model=LeadRead)
def add_activity(lead_id: str, payload: LeadActivityUpdate, db: Session = Depends(get_db), user: User = Depends(require_roles(*WRITE_ROLES))):
    lead = db.get(Lead, lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    db.add(LeadActivity(lead_id=lead.id, kind=payload.kind, note=payload.note, actor_id=user.id))
    if payload.next_action: lead.next_action = payload.next_action
    if payload.next_follow_up_at: lead.next_follow_up_at = payload.next_follow_up_at
    audit(db, user, "admissions.activity.create", "lead", lead.id, after={"kind": payload.kind}); db.commit(); db.refresh(lead)
    return lead


@router.post("/leads/{lead_id}/convert", response_model=ConversionResult)
def convert(lead_id: str, payload: ConversionRequest, db: Session = Depends(get_db), user: User = Depends(require_roles("owner", "admissions_manager"))):
    lead = db.get(Lead, lead_id)
    if not lead: raise HTTPException(404, "Lead not found")
    if lead.stage not in ("Admission Confirmed", "Converted"): raise HTTPException(409, "Lead must be Admission Confirmed before conversion")
    student, guardian, enrollment, finance = convert_lead(db, lead, payload, user)
    return {"leadId": lead.id, "studentId": student.id, "guardianId": guardian.id, "enrollmentId": enrollment.id, "financeHandoffId": finance.id}
