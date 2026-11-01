from pydantic import BaseModel, Field



class ProductBase(BaseModel):
    sku : str = Field(..., min_length=3, max_length=30, examples=["PROD-001"])
    name : str = Field(..., min_length=2, max_length=100, examples=["teclado hyper x"])
    unit_price : float = Field(..., gt=0, examples=["150.00"])
    description : str | None = Field(None, max_length=255, examples=["teclado RGB switch azul"])

class Product(ProductBase):
    pass
    

class ProductResponse(ProductBase):
    id: int 
    is_active : bool = True
    created_at : str
    updated_at : str | None = None


class ProductUpdate(BaseModel):
    sku: str | None = Field(None, min_length=3, max_length=30)
    name : str | None = Field(None, min_length=2, max_length= 100)
    description : str | None = Field(None, max_length=255)
    unit_price : float | None = Field(None, gt=0)
    is_active: bool | None = None