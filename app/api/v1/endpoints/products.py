from fastapi import FastAPI, status, HTTPException
from app.schemas.product import *
from decimal import Decimal
from app.services import product as product_services

 
app = FastAPI()

# listar produto
@app.get("/api/v1/products")
def get_products():
    return product_services.fetch_products()

# listar um produto
@app.get("/api/v1/products/{id}")
def get_produtc_by_id(id: int):
    return product_services.fetch_product(id)


@app.post("/api/v1/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in : Product):
    try:

        return product_services.register_product(product_in)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/v1//products/{id}")
def atualiza_products(id: int):
    pass

@app.patch("/api/v1/products/{id}/status")
def status_products(id: int):
    try :
        
        product_services.alterar_status(id)
    except Exception as e:
        raise ValueError("ocorreu um erro inesperado: {e}")






        


            


            

