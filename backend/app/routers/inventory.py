from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import InventoryItem, InventoryMovement, Student, User
from ..operations_schemas import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryMovementCreate,
)
from ..security import require_roles
from ..services import audit


router = APIRouter(prefix="/api/inventory", tags=["inventory"])
READ_ROLES = ("owner", "storekeeper", "accounts")
WRITE_ROLES = ("owner", "storekeeper")


def _serialize(row: InventoryItem):
    return {
        "id": row.id,
        "sku": row.sku,
        "name": row.name,
        "category": row.category,
        "unit": row.unit,
        "quantityOnHand": row.quantity_on_hand,
        "reorderLevel": row.reorder_level,
        "vendorReference": row.vendor_reference,
        "notes": row.notes,
        "sourceNote": row.source_note,
        "isActive": row.is_active,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
    }


def _movement(row: InventoryMovement, item: InventoryItem, actor: User):
    return {
        "id": row.id,
        "itemId": item.id,
        "itemName": item.name,
        "sku": item.sku,
        "movementType": row.movement_type,
        "quantityDelta": row.quantity_delta,
        "balanceAfter": row.balance_after,
        "occurredOn": row.occurred_on,
        "targetType": row.target_type,
        "targetReference": row.target_reference,
        "studentId": row.student_id,
        "reference": row.reference,
        "reason": row.reason,
        "createdBy": actor.full_name,
        "createdAt": row.created_at,
    }


@router.get("/bootstrap")
def bootstrap(
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*READ_ROLES)),
):
    rows = db.query(InventoryItem).order_by(
        InventoryItem.category,
        InventoryItem.name,
    ).all()
    active = [row for row in rows if row.is_active]
    recent = (
        db.query(InventoryMovement, InventoryItem, User)
        .join(InventoryItem, InventoryItem.id == InventoryMovement.item_id)
        .join(User, User.id == InventoryMovement.created_by)
        .order_by(InventoryMovement.created_at.desc())
        .limit(20)
        .all()
    )
    return {
        "items": [_serialize(row) for row in rows],
        "studentTargets": [
            {
                "id": student.id,
                "admissionNumber": student.admission_number,
                "fullName": student.full_name,
            }
            for student in db.query(Student)
            .filter(Student.status == "active")
            .order_by(Student.full_name)
            .all()
        ],
        "recentMovements": [_movement(*row) for row in recent],
        "summary": {
            "activeItems": len(active),
            "knownQuantities": sum(
                row.quantity_on_hand is not None for row in active
            ),
            "quantityPending": sum(
                row.quantity_on_hand is None for row in active
            ),
            "lowStock": sum(
                row.quantity_on_hand is not None
                and row.quantity_on_hand <= row.reorder_level
                for row in active
            ),
            "categories": len({row.category for row in active}),
        },
    }


@router.post("/items", status_code=201)
def create_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*WRITE_ROLES)),
):
    row = InventoryItem(
        sku=payload.sku.strip().upper(),
        name=payload.name.strip(),
        category=payload.category,
        unit=payload.unit.strip(),
        quantity_on_hand=payload.quantityOnHand,
        reorder_level=payload.reorderLevel,
        vendor_reference=(
            payload.vendorReference.strip()
            if payload.vendorReference
            else None
        ),
        notes=payload.notes.strip(),
        source_note="ERP entry",
        created_by=actor.id,
    )
    db.add(row)
    try:
        db.flush()
        if payload.quantityOnHand is not None:
            db.add(
                InventoryMovement(
                    item_id=row.id,
                    movement_type="opening",
                    quantity_delta=payload.quantityOnHand,
                    balance_after=payload.quantityOnHand,
                    occurred_on=row.created_at.date(),
                    target_type="department",
                    target_reference="Institute stock",
                    reference=None,
                    reason="Opening balance recorded with item creation",
                    created_by=actor.id,
                )
            )
        audit(
            db,
            actor,
            "inventory.item.create",
            "inventory_item",
            row.id,
            after=_serialize(row),
        )
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(409, "This inventory SKU already exists") from error
    return _serialize(row)


@router.patch("/items/{item_id}")
def update_item(
    item_id: str,
    payload: InventoryItemUpdate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*WRITE_ROLES)),
):
    row = db.get(InventoryItem, item_id)
    if not row:
        raise HTTPException(404, "Inventory item not found")
    opening_balance = (
        row.quantity_on_hand is None
        and payload.quantityOnHand is not None
    )
    if payload.quantityOnHand != row.quantity_on_hand and not opening_balance:
        raise HTTPException(
            409,
            detail={
                "code": "STOCK_MOVEMENT_REQUIRED",
                "message": (
                    "Stock quantity cannot be edited directly. "
                    "Record an inward, issue, return, write-off or adjustment."
                ),
            },
        )
    before = _serialize(row)
    row.name = payload.name.strip()
    row.category = payload.category
    row.unit = payload.unit.strip()
    if opening_balance:
        row.quantity_on_hand = payload.quantityOnHand
        db.add(
            InventoryMovement(
                item_id=row.id,
                movement_type="opening",
                quantity_delta=payload.quantityOnHand,
                balance_after=payload.quantityOnHand,
                occurred_on=row.updated_at.date(),
                target_type="department",
                target_reference="Institute stock",
                reference=None,
                reason=payload.notes.strip() or "Opening balance recorded",
                created_by=actor.id,
            )
        )
    row.reorder_level = payload.reorderLevel
    row.vendor_reference = (
        payload.vendorReference.strip()
        if payload.vendorReference
        else None
    )
    row.notes = payload.notes.strip()
    row.is_active = payload.isActive
    audit(
        db,
        actor,
        "inventory.item.update",
        "inventory_item",
        row.id,
        before=before,
        after=_serialize(row),
    )
    db.commit()
    return _serialize(row)


@router.get("/movements")
def list_movements(
    item_id: str | None = None,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*READ_ROLES)),
):
    query = (
        db.query(InventoryMovement, InventoryItem, User)
        .join(InventoryItem, InventoryItem.id == InventoryMovement.item_id)
        .join(User, User.id == InventoryMovement.created_by)
    )
    if item_id:
        query = query.filter(InventoryMovement.item_id == item_id)
    return [
        _movement(*row)
        for row in query.order_by(
            InventoryMovement.occurred_on.desc(),
            InventoryMovement.created_at.desc(),
        ).limit(500).all()
    ]


@router.post("/items/{item_id}/movements", status_code=201)
def create_movement(
    item_id: str,
    payload: InventoryMovementCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles(*WRITE_ROLES)),
):
    item = db.get(InventoryItem, item_id)
    if not item or not item.is_active:
        raise HTTPException(404, "Active inventory item not found")
    student = db.get(Student, payload.studentId) if payload.studentId else None
    if payload.studentId and not student:
        raise HTTPException(404, "Student not found")
    direction = {
        "inward": 1,
        "return": 1,
        "issue": -1,
        "write_off": -1,
    }.get(payload.movementType)
    delta = (
        payload.quantity
        if payload.movementType == "adjustment"
        else abs(payload.quantity) * direction
    )
    current = item.quantity_on_hand or 0
    balance = current + delta
    if balance < 0:
        raise HTTPException(
            409,
            detail={
                "code": "INSUFFICIENT_STOCK",
                "message": (
                    f"Only {current} {item.unit} are currently available"
                ),
            },
        )
    movement = InventoryMovement(
        item_id=item.id,
        movement_type=payload.movementType,
        quantity_delta=delta,
        balance_after=balance,
        occurred_on=payload.occurredOn,
        target_type=payload.targetType,
        target_reference=(
            payload.targetReference.strip()
            if payload.targetReference
            else student.full_name
            if student
            else None
        ),
        student_id=student.id if student else None,
        reference=payload.reference.strip() if payload.reference else None,
        reason=payload.reason.strip(),
        created_by=actor.id,
    )
    item.quantity_on_hand = balance
    db.add(movement)
    db.flush()
    audit(
        db,
        actor,
        "inventory.movement.create",
        "inventory_movement",
        movement.id,
        after={
            "itemId": item.id,
            "movementType": movement.movement_type,
            "quantityDelta": movement.quantity_delta,
            "balanceAfter": movement.balance_after,
            "studentId": movement.student_id,
            "reference": movement.reference,
            "reason": movement.reason,
        },
    )
    db.commit()
    return _movement(movement, item, actor)
