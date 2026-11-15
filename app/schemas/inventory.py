from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.core.enums import MovementType


class InventoryResponse(BaseModel):
    product_id: int
    quantity_on_hand: int

    model_config = ConfigDict(from_attributes=True)


class MovementCreate(BaseModel):
    quantity: int = Field(..., gt=0)
    movement_type: MovementType
    reason: str = Field(..., min_length=1, max_length=255)


class MovementResponse(BaseModel):
    id: int
    product_id: int
    order_id: int | None = None
    movement_type: MovementType
    quantity_delta: int
    reason: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
