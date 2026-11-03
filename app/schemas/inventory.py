from pydantic import BaseModel, Field
from decimal import Decimal


class InventoryResponse(BaseModel):
    product_id: int
    quantity_on_hand: int


class MovementCreate(BaseModel):
    quantity: int = Field(..., gt=0)
    movement_type: str = Field(..., pattern="^(in|out|adjustment)$")
    reason: str = Field(..., min_length=1)
