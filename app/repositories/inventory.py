from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.time import utc_now
from app.models.inventory import Inventory


def find_all(db: Session) -> list[Inventory]:
    return list(db.scalars(select(Inventory).order_by(Inventory.product_id)).all())


def find_by_product_id(db: Session, product_id: int) -> Inventory | None:
    return db.get(Inventory, product_id)


def get_or_create(db: Session, product_id: int, initial_quantity: int = 0) -> Inventory:
    inventory = db.get(Inventory, product_id)
    if inventory is None:
        inventory = Inventory(
            product_id=product_id,
            quantity_on_hand=initial_quantity,
        )
        db.add(inventory)
        db.flush()
    return inventory


def set_quantity(db: Session, product_id: int, quantity: int) -> Inventory:
    inventory = get_or_create(db, product_id)
    inventory.quantity_on_hand = quantity
    inventory.updated_at = utc_now()
    db.flush()
    return inventory


def increment(db: Session, product_id: int, quantity: int) -> bool:
    result = db.execute(
        update(Inventory)
        .where(Inventory.product_id == product_id)
        .values(
            quantity_on_hand=Inventory.quantity_on_hand + quantity,
            updated_at=utc_now(),
        )
    )
    return result.rowcount == 1


def try_decrement(db: Session, product_id: int, quantity: int) -> bool:
    """Atomically decrement only when enough stock exists."""
    result = db.execute(
        update(Inventory)
        .where(
            Inventory.product_id == product_id,
            Inventory.quantity_on_hand >= quantity,
        )
        .values(
            quantity_on_hand=Inventory.quantity_on_hand - quantity,
            updated_at=utc_now(),
        )
    )
    return result.rowcount == 1
