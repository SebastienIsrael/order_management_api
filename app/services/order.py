import hashlib
import json
import uuid
from decimal import Decimal

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import MovementType, OrderStatus
from app.core.exceptions import ConflictError, NotFoundError, UnprocessableEntityError
from app.models.inventory_movement import InventoryMovement
from app.models.order import Order, OrderItem
from app.repositories import inventory as inventory_repo
from app.repositories import inventory_movements as movements_repo
from app.repositories import orders as orders_repo
from app.repositories import products as products_repo
from app.schemas.order import OrderCreate, OrderItemCreate


def _consolidate_items(items: list[OrderItemCreate]) -> dict[int, int]:
    consolidated: dict[int, int] = {}
    for item in items:
        if item.quantity <= 0:
            raise UnprocessableEntityError("INVALID_QUANTITY")
        consolidated[item.product_id] = consolidated.get(item.product_id, 0) + item.quantity
    return consolidated


def _request_fingerprint(
    order_in: OrderCreate, consolidated: dict[int, int]
) -> str:
    payload = {
        "customer_reference": order_in.customer_reference,
        "items": [
            {"product_id": product_id, "quantity": quantity}
            for product_id, quantity in sorted(consolidated.items())
        ],
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _get_order_or_404(db: Session, order_id: int) -> Order:
    order = orders_repo.find_by_id(db, order_id)
    if order is None:
        raise NotFoundError("Order not found")
    return order


def create_order(
    db: Session,
    order_in: OrderCreate,
    idempotency_key: str | None = None,
) -> Order:
    key = idempotency_key.strip() if idempotency_key else None
    consolidated = _consolidate_items(order_in.items)
    if not consolidated:
        raise UnprocessableEntityError("EMPTY_ORDER")

    fingerprint = _request_fingerprint(order_in, consolidated)

    if key is not None:
        existing = orders_repo.find_by_idempotency_key(db, key)
        if existing is not None:
            if existing.request_fingerprint != fingerprint:
                raise ConflictError("Idempotency key reused with a different payload")
            return existing

    details: list[dict] = []
    for product_id, quantity in consolidated.items():
        product = products_repo.find_by_id(db, product_id)
        if product is None:
            raise NotFoundError("Product not found")
        if not product.is_active:
            raise ConflictError("Product inactive")

        inventory = inventory_repo.find_by_product_id(db, product_id)
        available = inventory.quantity_on_hand if inventory is not None else 0
        if available < quantity:
            raise ConflictError("Insufficient stock")

        unit_price = product.unit_price
        details.append(
            {
                "product_id": product_id,
                "product_name": product.name,
                "quantity": quantity,
                "unit_price": unit_price,
                "line_total": unit_price * quantity,
            }
        )

    total_amount = sum(
        (detail["line_total"] for detail in details), Decimal("0.00")
    )
    order = Order(
        order_number=f"ORD-{uuid.uuid4().hex[:12].upper()}",
        customer_reference=order_in.customer_reference,
        status=OrderStatus.CONFIRMED,
        total_amount=total_amount,
        idempotency_key=key,
        request_fingerprint=fingerprint if key is not None else None,
        items=[
            OrderItem(
                product_id=detail["product_id"],
                product_name=detail["product_name"],
                quantity=detail["quantity"],
                unit_price=detail["unit_price"],
                line_total=detail["line_total"],
            )
            for detail in details
        ],
    )

    try:
        orders_repo.add(db, order)

        for detail in details:
            if not inventory_repo.try_decrement(
                db, detail["product_id"], detail["quantity"]
            ):
                raise ConflictError("Insufficient stock")
            movements_repo.add(
                db,
                InventoryMovement(
                    product_id=detail["product_id"],
                    order_id=order.id,
                    movement_type=MovementType.OUT,
                    quantity_delta=-detail["quantity"],
                    reason="order_created",
                ),
            )

        db.commit()
    except IntegrityError:
        db.rollback()
        if key is not None:
            existing = orders_repo.find_by_idempotency_key(db, key)
            if existing is not None:
                if existing.request_fingerprint != fingerprint:
                    raise ConflictError(
                        "Idempotency key reused with a different payload"
                    ) from None
                return existing
        raise ConflictError("Could not create order") from None
    except Exception:
        db.rollback()
        raise

    return order


def list_orders(
    db: Session, status_filter: OrderStatus | None = None
) -> list[Order]:
    return orders_repo.find_all(db, status_filter=status_filter)


def get_order(db: Session, order_id: int) -> Order:
    return _get_order_or_404(db, order_id)


def cancel_order(db: Session, order_id: int) -> Order:
    order = _get_order_or_404(db, order_id)

    if order.status == OrderStatus.CANCELLED:
        raise ConflictError("Order already cancelled")
    if order.status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
        raise ConflictError("Order not eligible for cancellation")

    try:
        if not orders_repo.try_mark_cancelled(db, order_id):
            db.rollback()
            current = orders_repo.find_by_id(db, order_id)
            if current is not None and current.status == OrderStatus.CANCELLED:
                raise ConflictError("Order already cancelled")
            raise ConflictError("Order not eligible for cancellation")

        for item in order.items:
            inventory_repo.get_or_create(db, item.product_id, initial_quantity=0)
            if not inventory_repo.increment(db, item.product_id, item.quantity):
                raise ConflictError("Product not found")
            movements_repo.add(
                db,
                InventoryMovement(
                    product_id=item.product_id,
                    order_id=order.id,
                    movement_type=MovementType.IN,
                    quantity_delta=item.quantity,
                    reason="order_cancelled",
                ),
            )

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order
