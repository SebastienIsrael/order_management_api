from pydantic import BaseModel

class Product(BaseModel):
    sku : str
    name : str
    unit_price : float
    description : str | None = None
    

class ProductResponse(BaseModel):
    id: int 
    is_active : bool = True