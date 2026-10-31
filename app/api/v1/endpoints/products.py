from fastapi import FastAPI, status, HTTPException
from app.schemas.product import *
from decimal import Decimal
from app.services import product as product_services

 
app = FastAPI()

# get all products
@app.get("/api/v1/products", response_model=list[ProductResponse], status_code=status.HTTP_200_OK)
def get_products():
    return product_services.fetch_products()

# get all product
@app.get("/api/v1/products/{id}", response_model=ProductResponse,status_code=status.HTTP_200_OK)
def get_produtc_by_id(id: int):
    return product_services.fetch_product(id)

# create new product
@app.post("/api/v1/products", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(product_in : Product):
    try:
        return product_services.register_product(product_in)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

# alter product
@app.patch("/api/v1/products/{product_id}", response_model=ProductResponse,status_code=status.HTTP_200_OK )
def atualiza_products(product_id: int, product_update: ProductUpdate):
    try:
        return product_services.update_product(product_id, product_update)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# alter status on ptoduct 
@app.patch("/api/v1/products/{id}/status", response_model=ProductResponse,status_code=status.HTTP_200_OK)
def status_products(id: int):
    try :   
        return product_services.toogle_status(id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# product_services.update_product(11,{ "sku": "TEST-003",
#   "name": "teclado hyper x",
#   "description": "usado",
#   "unit_price": 250,
#   "is_active": True})



        


            


            

