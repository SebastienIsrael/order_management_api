from sqlalchemy.orm import Session

from app.core.enums import MovementType
from app.core.exceptions import ConflictError, NotFoundError, UnprocessableEntityError
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.repositories import inventory as inventory_repo
from app.repositories import inventory_movements as movements_repo
from app.repositories import products as products_repo
from app.schemas.inventory import MovementCreate


def _require_product(db: Session, product_id: int) -> None:
    if products_repo.find_by_id(db, product_id) is None:
        raise NotFoundError("Product not found")


def get_inventory(db: Session, product_id: int) -> Inventory:
    _require_product(db, product_id)
    inventory = inventory_repo.find_by_product_id(db, product_id)
    if inventory is None:
        inventory = inventory_repo.get_or_create(db, product_id, initial_quantity=0)
        db.commit()
        db.refresh(inventory)
    return inventory


def add_movement(db: Session, product_id: int, movement_in: MovementCreate) -> Inventory:
    _require_product(db, product_id)

    if movement_in.quantity <= 0:
        raise UnprocessableEntityError("INVALID_QUANTITY")

    try:
        if movement_in.movement_type == MovementType.OUT:
            if not inventory_repo.try_decrement(db, product_id, movement_in.quantity):
                raise ConflictError("Insufficient stock")
            quantity_delta = -movement_in.quantity
        else:
            # `in` adds stock; `adjustment` keeps the original V1 semantics:
            # a positive adjustment is treated as an inbound movement.
            if not inventory_repo.increment(db, product_id, movement_in.quantity):
                inventory_repo.get_or_create(db, product_id, initial_quantity=0)
                inventory_repo.increment(db, product_id, movement_in.quantity)
            quantity_delta = movement_in.quantity

        movement = InventoryMovement(
            product_id=product_id,
            order_id=None,
            movement_type=movement_in.movement_type,
            quantity_delta=quantity_delta,
            reason=movement_in.reason,
        )
        movements_repo.add(db, movement)
        db.commit()
    except Exception:
        db.rollback()
        raise

    inventory = inventory_repo.find_by_product_id(db, product_id)
    if inventory is not None:
        db.refresh(inventory)
    return inventory


def get_movements(db: Session, product_id: int) -> list[InventoryMovement]:
    _require_product(db, product_id)
    return movements_repo.find_by_product_id(db, product_id)
