from pydantic import BaseModel
from decimal import Decimal

class Product(BaseModel):
    sku : str
    name : str
    unit_price : float
    description : str | None = None
    

class ProductResponse(Product):
    id: int 
    is_active : bool = True
    created_at : str
    update_at : str | None


class ProductUpdate(Product):
    sku: str | None
    name : str | None
    description : str | None
    unit_price : float | None
    is_active: bool | None = None