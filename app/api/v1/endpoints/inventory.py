from fastapi import APIRouter, status, HTTPException

from app.schemas.inventory import InventoryResponse, MovementCreate
from app.services import inventory as inventory_service

router = APIRouter(prefix="/inventory", tags=["inventory"])


@router.get("/{product_id}", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def get_inventory(product_id: int):
    try:
        return inventory_service.get_inventory(product_id)
    except ValueError as e:
        if str(e) == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/{product_id}/movements", response_model=InventoryResponse, status_code=status.HTTP_200_OK)
def create_movement(product_id: int, movement_in: MovementCreate):
    try:
        return inventory_service.add_movement(product_id, movement_in)
    except ValueError as e:
        msg = str(e)
        if msg == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        if msg == "INSUFFICIENT_STOCK":
            raise HTTPException(status_code=409, detail="Insufficient stock")
        raise HTTPException(status_code=422, detail=msg)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/{product_id}/movements", status_code=status.HTTP_200_OK)
def get_movements(product_id: int):
    try:
        return inventory_service.get_movements(product_id)
    except ValueError as e:
        if str(e) == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
