from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.core.enums import OrderStatus
from app.core.time import utc_now
from app.models.order import Order


def find_all(db: Session, status_filter: OrderStatus | None = None) -> list[Order]:
    statement = select(Order).order_by(Order.id)
    if status_filter is not None:
        statement = statement.where(Order.status == status_filter)
    return list(db.scalars(statement).all())


def find_by_id(db: Session, order_id: int) -> Order | None:
    return db.get(Order, order_id)


def find_by_idempotency_key(db: Session, key: str) -> Order | None:
    return db.scalar(select(Order).where(Order.idempotency_key == key))


def add(db: Session, order: Order) -> Order:
    db.add(order)
    db.flush()
    return order


def try_mark_cancelled(db: Session, order_id: int) -> bool:
    """Atomically cancel only an order that is still cancellable."""
    result = db.execute(
        update(Order)
        .where(
            Order.id == order_id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED]),
        )
        .values(status=OrderStatus.CANCELLED, updated_at=utc_now())
    )
    return result.rowcount == 1
