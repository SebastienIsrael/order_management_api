from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.inventory_movement import InventoryMovement


def add(db: Session, movement: InventoryMovement) -> InventoryMovement:
    db.add(movement)
    db.flush()
    return movement


def find_by_product_id(db: Session, product_id: int) -> list[InventoryMovement]:
    statement = (
        select(InventoryMovement)
        .where(InventoryMovement.product_id == product_id)
        .order_by(InventoryMovement.created_at, InventoryMovement.id)
    )
    return list(db.scalars(statement).all())
