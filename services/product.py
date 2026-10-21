import json
from pathlib import Path
from datetime import datetime, timezone







class OperationFile:

    caminho = Path(__file__).parent / 'db' / 'products_db.json'
    def __init__(self):
        self.current_time = datetime.now(timezone.utc).isoformat()
        with open(self.caminho, 'r', encoding='utf-8') as f:
            self.produtos = json.load(f)

    def save_alteration(self):
        with open(self.caminho, 'w', encoding='utf-8') as arquivo_saida:
            json.dump(self.produtos, arquivo_saida, ensure_ascii=False, indent=2)
            return True
            
    def view_products(self):
        string = ''
        for item in self.produtos:
            string += f'{item}\n'
        return string
    def view_product(self, id):
        for i, item in enumerate(self.produtos):
            print(item['id'])
            if item['id'] == id:
                return f'{item}'

    def adicionar_produto(self, p):
        p.update({"created_at": self.current_time, "updated_at": None})
        self.produtos.append(p)
        self.save_alteration()

    

   






    


