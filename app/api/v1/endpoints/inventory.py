from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inventory import InventoryResponse, MovementCreate, MovementResponse
from app.services import inventory as inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get(
    "/{product_id}",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
def get_inventory(product_id: int, db: Session = Depends(get_db)):
    return inventory_service.get_inventory(db, product_id)


@router.post(
    "/{product_id}/movements",
    response_model=InventoryResponse,
    status_code=status.HTTP_200_OK,
)
def create_movement(
    product_id: int,
    movement_in: MovementCreate,
    db: Session = Depends(get_db),
):
    return inventory_service.add_movement(db, product_id, movement_in)


@router.get(
    "/{product_id}/movements",
    response_model=list[MovementResponse],
    status_code=status.HTTP_200_OK,
)
def get_movements(product_id: int, db: Session = Depends(get_db)):
    return inventory_service.get_movements(db, product_id)
