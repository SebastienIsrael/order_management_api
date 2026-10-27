from pathlib import Path
import json
import os
import tempfile
import copy

file_path = Path(__file__).resolve().parent.parent / "db" / "products_db.json"
_data = None
def _load():
    
    global _data
    if _data is None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data_content = f.read()
               
                _data = json.loads(data_content) if data_content.strip() else []

        except FileNotFoundError:
             _data = []
    return _data
                

def _save():
    global _data
    dir_name = os.path.dirname(file_path) or '.'
    
    try:
        fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
                json.dump(_data, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, file_path)

    except Exception:
         os.unlink(tmp_path)
         raise
    
def read_data():
     return copy.deepcopy(_load())

def find_by_id(id: int) -> dict | None:
     _load()
     for product in _data:
          if product['id'] == id:
               return copy.deepcopy(product)
          return None
     
def add_data(new_data):
     global _data
     _load()
     _data.append(new_data)
     _save()

def alter_status(id: int):
     global _data
     for d in _data:
          if d['id'] == id:
               d['is_active'] = False if d['is_active'] else True
               _save()
               return 
def update(id: int, updated_product: dict) -> bool:
     global _data 
     for data in _data:
          if data["id"] == id:
               data.update(updated_product)
               _save()
     return False
    

    
    