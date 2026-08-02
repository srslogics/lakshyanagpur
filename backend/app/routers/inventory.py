from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
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


def _student_stock(db: Session, student: Student):
    rows = (
        db.query(InventoryMovement, InventoryItem, User)
        .join(InventoryItem, InventoryItem.id == InventoryMovement.item_id)
        .join(User, User.id == InventoryMovement.created_by)
        .filter(
            InventoryMovement.student_id == student.id,
            InventoryMovement.movement_type.in_(("issue", "return")),
        )
        .order_by(
            InventoryMovement.occurred_on.desc(),
            InventoryMovement.created_at.desc(),
        )
        .all()
    )
    holdings = {}
    for movement, item, _ in rows:
        holding = holdings.setdefault(
            item.id,
            {
                "itemId": item.id,
                "itemName": item.name,
                "sku": item.sku,
                "category": item.category,
                "unit": item.unit,
                "quantityIssued": 0,
                "lastIssuedOn": None,
            },
        )
        holding["quantityIssued"] -= movement.quantity_delta
        if movement.movement_type == "issue" and (
            holding["lastIssuedOn"] is None
            or movement.occurred_on > holding["lastIssuedOn"]
        ):
            holding["lastIssuedOn"] = movement.occurred_on
    active_holdings = sorted(
        (
            holding
            for holding in holdings.values()
            if holding["quantityIssued"] > 0
        ),
        key=lambda holding: (holding["category"], holding["itemName"]),
    )
    available = (
        db.query(InventoryItem)
        .filter(InventoryItem.is_active.is_(True))
        .order_by(InventoryItem.category, InventoryItem.name)
        .all()
    )
    return {
        "studentId": student.id,
        "studentName": student.full_name,
        "admissionNumber": student.admission_number,
        "holdings": active_holdings,
        "history": [_movement(*row) for row in rows],
        "availableItems": [_serialize(row) for row in available],
        "summary": {
            "itemTypes": len(active_holdings),
            "issuedUnits": sum(
                holding["quantityIssued"] for holding in active_holdings
            ),
            "transactions": len(rows),
        },
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
    student_balances = (
        db.query(
            InventoryMovement.student_id,
            InventoryMovement.item_id,
            func.sum(InventoryMovement.quantity_delta),
        )
        .filter(
            InventoryMovement.student_id.is_not(None),
            InventoryMovement.movement_type.in_(("issue", "return")),
        )
        .group_by(InventoryMovement.student_id, InventoryMovement.item_id)
        .all()
    )
    issued_balances = [
        (student_id, max(0, -int(balance or 0)))
        for student_id, _, balance in student_balances
    ]
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
            "issuedToStudents": sum(
                balance for _, balance in issued_balances
            ),
            "studentsWithItems": len({
                student_id
                for student_id, balance in issued_balances
                if balance > 0
            }),
        },
    }


@router.get("/students/{student_id}")
def student_stock(
    student_id: str,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(*READ_ROLES)),
):
    student = db.get(Student, student_id)
    if not student or student.is_test_account:
        raise HTTPException(404, "Student not found")
    return _student_stock(db, student)


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
    item = (
        db.query(InventoryItem)
        .filter(InventoryItem.id == item_id)
        .with_for_update()
        .one_or_none()
    )
    if not item or not item.is_active:
        raise HTTPException(404, "Active inventory item not found")
    student = db.get(Student, payload.studentId) if payload.studentId else None
    if payload.studentId and (not student or student.is_test_account):
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
    if student and payload.movementType == "return":
        student_balance = (
            db.query(
                func.coalesce(func.sum(InventoryMovement.quantity_delta), 0)
            )
            .filter(
                InventoryMovement.item_id == item.id,
                InventoryMovement.student_id == student.id,
                InventoryMovement.movement_type.in_(("issue", "return")),
            )
            .scalar()
        )
        outstanding = max(0, -int(student_balance or 0))
        if payload.quantity > outstanding:
            raise HTTPException(
                409,
                detail={
                    "code": "RETURN_EXCEEDS_STUDENT_BALANCE",
                    "message": (
                        f"Only {outstanding} {item.unit} are currently issued "
                        f"to {student.full_name}"
                    ),
                },
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
