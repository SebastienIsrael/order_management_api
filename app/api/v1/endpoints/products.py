from fastapi import FastAPI, status
from app.schemas.product import *
from decimal import Decimal
from services.product import OperationFile

 
app = FastAPI()

# listar produto
@app.get("/api/v1/products")
def get_products():
    return OperationFile().view_products()

# listar um produto
@app.get("/api/v1/products/{id}")
def get_produtc_by_id(id: int):
    return OperationFile().view_product(id)


@app.post("/api/v1/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def add_produtc(product_in : Product):
    return OperationFile().adicionar_produto({
        
        "sku": product_in.sku,
        "name": product_in.name,
        "description": product_in.description,
        "unit_price": product_in.unit_price,
        "is_active": True
        
    })









        


            


            

