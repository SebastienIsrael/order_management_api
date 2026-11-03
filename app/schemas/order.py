from pydantic import BaseModel, Field
from decimal import Decimal
from typing import List


class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(..., gt=0)


class OrderCreate(BaseModel):
    customer_reference: str = Field(..., min_length=1)
    items: List[OrderItemCreate] = Field(..., min_length=1)


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_reference: str
    status: str
    total_amount: Decimal
    items: List[OrderItemResponse] = []
    created_at: str
    updated_at: str | None = None
