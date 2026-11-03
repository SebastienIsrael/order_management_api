from fastapi import APIRouter, status, HTTPException

from app.schemas.product import Product, ProductResponse, ProductUpdate
from app.services import product as product_services

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
@router.get("", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products():
    return product_services.fetch_products()


@router.get("/{id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def get_product_by_id(id: int):
    try:
        return product_services.fetch_product(id)
    except ValueError as e:
        if str(e) == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=400, detail=str(e))


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in: Product):
    try:
        return product_services.register_product(product_in)
    except ValueError as e:
        msg = str(e)
        if msg == "SKU_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail="SKU already exists")
        if msg.startswith("falha ao salvar"):
            raise HTTPException(status_code=500, detail="Internal server error")
        raise HTTPException(status_code=422, detail=msg)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{product_id}", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def update_product(product_id: int, product_update: ProductUpdate):
    try:
        result = product_services.update_product(product_id, product_update)
        if result is None:
            return product_services.fetch_product(product_id)
        return result
    except ValueError as e:
        msg = str(e)
        if msg == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        if msg == "SKU_ALREADY_EXISTS":
            raise HTTPException(status_code=409, detail="SKU already exists")
        raise HTTPException(status_code=422, detail=msg)
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


@router.patch("/{id}/status", response_model=ProductResponse, status_code=status.HTTP_200_OK)
def status_products(id: int):
    try:
        return product_services.toogle_status(id)
    except ValueError as e:
        if str(e) == "PROD_NOT_FOUND":
            raise HTTPException(status_code=404, detail="Product not found")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
