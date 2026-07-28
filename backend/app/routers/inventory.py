from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import InventoryItem, User
from ..operations_schemas import InventoryItemCreate, InventoryItemUpdate
from ..security import require_roles
from ..services import audit


router = APIRouter(prefix="/api/inventory", tags=["inventory"])
READ_ROLES = ("owner", "storekeeper")


def _serialize(row: InventoryItem):
    return {
        "id": row.id,
        "sku": row.sku,
        "name": row.name,
        "category": row.category,
        "unit": row.unit,
        "quantityOnHand": row.quantity_on_hand,
        "notes": row.notes,
        "sourceNote": row.source_note,
        "isActive": row.is_active,
        "createdAt": row.created_at,
        "updatedAt": row.updated_at,
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
    return {
        "items": [_serialize(row) for row in rows],
        "summary": {
            "activeItems": len(active),
            "knownQuantities": sum(
                row.quantity_on_hand is not None for row in active
            ),
            "quantityPending": sum(
                row.quantity_on_hand is None for row in active
            ),
            "categories": len({row.category for row in active}),
        },
    }


@router.post("/items", status_code=201)
def create_item(
    payload: InventoryItemCreate,
    db: Session = Depends(get_db),
    actor: User = Depends(require_roles("owner")),
):
    row = InventoryItem(
        sku=payload.sku.strip().upper(),
        name=payload.name.strip(),
        category=payload.category,
        unit=payload.unit.strip(),
        quantity_on_hand=payload.quantityOnHand,
        notes=payload.notes.strip(),
        source_note="ERP entry",
        created_by=actor.id,
    )
    db.add(row)
    try:
        db.flush()
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
    actor: User = Depends(require_roles("owner")),
):
    row = db.get(InventoryItem, item_id)
    if not row:
        raise HTTPException(404, "Inventory item not found")
    before = _serialize(row)
    row.name = payload.name.strip()
    row.category = payload.category
    row.unit = payload.unit.strip()
    row.quantity_on_hand = payload.quantityOnHand
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
