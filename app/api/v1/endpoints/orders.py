from typing import Optional

from fastapi import APIRouter, Depends, Header, Query, status
from sqlalchemy.orm import Session

from app.core.enums import OrderStatus
from app.db.session import get_db
from app.schemas.order import OrderCreate, OrderResponse
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_in: OrderCreate,
    idempotency_key: Optional[str] = Header(
        None, alias="Idempotency-Key", max_length=255
    ),
    db: Session = Depends(get_db),
):
    return order_service.create_order(
        db, order_in, idempotency_key=idempotency_key
    )


@router.get("", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
@router.get("/", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
def list_orders(
    status_filter: OrderStatus | None = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return order_service.list_orders(db, status_filter=status_filter)


@router.get("/{order_id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.get_order(db, order_id)


@router.post(
    "/{order_id}/cancel",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    return order_service.cancel_order(db, order_id)
