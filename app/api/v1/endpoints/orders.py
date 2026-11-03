from fastapi import APIRouter, status, HTTPException, Header
from typing import Optional

from app.schemas.order import OrderCreate, OrderResponse
from app.services import order as order_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(order_in: OrderCreate, idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key")):
    try:
        return order_service.create_order(order_in, idempotency_key=idempotency_key)
    except ValueError as e:
        msg = str(e)
        if msg == "PRODUCT_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        if msg == "PRODUCT_INACTIVE":
            raise HTTPException(status_code=409, detail="Product inactive")
        if msg == "INSUFFICIENT_STOCK":
            raise HTTPException(status_code=409, detail="Insufficient stock")
        if msg in ("EMPTY_ORDER", "INVALID_QUANTITY"):
            raise HTTPException(status_code=422, detail=msg)
        raise HTTPException(status_code=422, detail=msg)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
@router.get("/", response_model=list[OrderResponse], status_code=status.HTTP_200_OK)
def list_orders(status: Optional[str] = None):
    try:
        return order_service.list_orders(status_filter=status)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{id}", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def get_order(id: int):
    try:
        return order_service.get_order(id)
    except ValueError as e:
        if str(e) == "ORDER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Order not found")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/{id}/cancel", response_model=OrderResponse, status_code=status.HTTP_200_OK)
def cancel_order(id: int):
    try:
        return order_service.cancel_order(id)
    except ValueError as e:
        msg = str(e)
        if msg == "ORDER_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Order not found")
        if msg == "ALREADY_CANCELLED":
            raise HTTPException(status_code=409, detail="Order already cancelled")
        if msg == "NOT_ELIGIBLE":
            raise HTTPException(status_code=409, detail="Order not eligible for cancellation")
        raise HTTPException(status_code=422, detail=msg)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
