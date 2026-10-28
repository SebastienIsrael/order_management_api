
from app.repositories import products as repository_product
from app.schemas.product import Product, ProductUpdate
from datetime import datetime, timezone


products = repository_product.find_all()

current_time = datetime.now(timezone.utc).isoformat(). replace('+00:00', 'Z')

def fetch_products():
       if not products:
           raise ValueError('internal server error.')
       return products

def fetch_product(id: int):
      product = repository_product.find_by_id(id)
      if not product:
            raise ValueError('Product id not found')
      return product

            
def register_product(product_in: Product):
            try:  
                  for product in products:
                        if product["sku"] == product_in.sku:
                              raise ValueError('sku não pode ser duplicado')
                  product = {
                              "id": len(products)+ 1,
                              "sku": product_in.sku,
                              "name": product_in.name,
                              "description":  product_in.description,
                              "unit_price": product_in.unit_price,
                              "is_active":True,
                              "created_at": current_time,
                              "updated_at": None
                  }
                  
                  repository_product.add_product(product)
            except Exception as e:
                   raise ValueError(f"falha ao salvar o product :{e}")
      
def update_product(product_in: ProductUpdate, product_id : int):
      product = repository_product.find_by_id(product_id)
      if not product:
            raise ValueError('product id not found')

      update_data = product_in.model_dump(exclude_unset=True)

      if not update_data:
            return 
      product.update(update_data)
      repository_product.update_product(products)
      

def toogle_status(product_id: int):
      product = repository_product.find_by_id(product_id)
      if not  product :
            raise ValueError('product id not found')

      product['is_active'] = not product["is_active"]

      repository_product.update_product(product_id, product)




   






    


