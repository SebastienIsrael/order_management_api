
from app.repositories import products as repository_product
from app.schemas.product import Product, ProductUpdate
from datetime import datetime, timezone



def _get_utc_now() -> str:
      return datetime.now(timezone.utc).isoformat(). replace('+00:00', 'Z')

def fetch_products():
       return repository_product.find_all()

def fetch_product(id: int):
      product = repository_product.find_by_id(id)
      if not product:
            raise ValueError("PROD_NOT_FOUND")
      return product

            
def register_product(product_in: Product):
            products = repository_product.find_all()
            try:  
                  for p in products:
                        if p["sku"] == product_in.sku:
                              raise ValueError("SKU_ALREADY_EXISTS")
                  new_id = max([p["id"]for p in products], default=0) + 1
                  product = {
                              "id": new_id,
                              "sku": product_in.sku,
                              "name": product_in.name,
                              "description":  product_in.description,
                              "unit_price": product_in.unit_price,
                              "is_active":True,
                              "created_at": _get_utc_now(),
                              "updated_at": None
                  }
                  
                  repository_product.add_product(product)
                  return product
            except Exception as e:
                   raise ValueError(f"falha ao salvar o product :{e}")
      
def update_product(product_id : int, product_in: ProductUpdate):
      product = repository_product.find_by_id(product_id)
      if not product:
            raise ValueError("PROD_NOT_FOUND")

      updated_product = product_in.model_dump(exclude_unset=True)

      if not updated_product:
            return 
      if "sku" in updated_product:
            products = repository_product.find_all()
            SKU_duplicado = any(
                  p["sku"] == updated_product["sku"] and p["id"] != product_id
                  for p in products
                  )
            if SKU_duplicado:
                  raise ValueError("SKU_ALREADY_EXISTS")
      updated_product["updated_at"] = _get_utc_now()

      repository_product.update_product(product_id, updated_product)
      return product
      

def toogle_status(product_id: int):
      product = repository_product.find_by_id(product_id)
      if not  product :
            raise ValueError("PROD_NOT_FOUND")

      updated_product = {
             "is_active": not product["is_active"],
             "updated_at": _get_utc_now()
                                      
      }

      repository_product.update_product(product_id, updated_product)
      return repository_product.find_by_id(product_id)




   






    


