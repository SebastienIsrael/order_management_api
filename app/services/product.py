
from app.repositories import products as repository_product
from app.schemas.product import Product, ProductUpdate
from datetime import datetime, timezone


products = repository_product.read_data()
current_time = datetime.now(timezone.utc).isoformat(). replace('+00:00', 'Z')

def fetch_products():
       if not products:
           pass
       return products

def fetch_product(id: int):
      for product in products:
            if product['id'] == id:
                  return product

            
def register_product(product_in: Product):
            try:
                   
                  for product in products:
                        if product["sku"] == product_in.sku:
                              raise ValueError("sku não pode ser duplicado")
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
                  
                  repository_product.add_data(product)
            except Exception as e:
                   raise ValueError(f"falha ao salvar o product :{e}")
      
def update_product(product_in: ProductUpdate):
      update_data = product_in.model_dump(exclude_unset=True)

      if not update_data:
            return 
      

def toogle_status(id: int):
      for product in products:
            if product["id"] == id:
                  try :
                        repository_product.alter_status(id)  
                  except Exception as e:
                        raise ValueError(f"ocorreu um erro inesperado: {e}")
            else:
                  raise ValueError(f"'ID' not found")
                   





   






    


