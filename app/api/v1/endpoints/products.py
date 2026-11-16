from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import Product, ProductResponse, ProductUpdate
from app.services import product as product_service

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
@router.get("", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products(db: Session = Depends(get_db)):
    return product_service.fetch_products(db)


@router.get("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)):
    return product_service.fetch_product(db, product_id)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: Product, db: Session = Depends(get_db)):
    return product_service.register_product(db, product_in)


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(
    product_id: int,
    product_update: ProductUpdate,
    db: Session = Depends(get_db),
):
    return product_service.update_product(db, product_id, product_update)


@router.patch(
    "/{product_id}/status",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
)
def toggle_product_status(product_id: int, db: Session = Depends(get_db)):
    return product_service.toggle_status(db, product_id)
