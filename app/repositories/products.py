from pathlib import Path
import json
import os
import tempfile
import copy

file_path = Path(__file__).resolve().parent.parent / "db" / "products_db.json"
_products = None

def _load() -> list[dict]:
    
    global _products
    if _products is None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                json_content = f.read()  
                _products = json.loads(json_content) if json_content.strip() else []

        except FileNotFoundError:
             _products = []
    return _products
                
def _save() -> None:
    global _products

    try:
        dir_name = os.path.dirname(file_path) or '.'
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(_products, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, file_path)

    except Exception:
         os.unlink(tmp_path)
         raise

def _find_raw(product_id: int) -> dict | None:
     _load()
     for product in _products:
          if product['id'] == product_id:
               return product
     return None

def find_all() -> list[dict]:
     return copy.deepcopy(_load())
  
def find_by_id(product_id: int) -> dict | None:
     return copy.deepcopy(_find_raw(product_id))

def add_product(new_product: dict) -> None:
     global _products
     try:
          _load()
          _products.append(new_product)
          _save()
     except Exception:
          return False
     

def update_product(product_id: int, updated_product: dict) -> bool:
     global _products 
     product = _find_raw(product_id)
     if not  product:
          return False

     product.update(updated_product)
     _save()
     return True
     