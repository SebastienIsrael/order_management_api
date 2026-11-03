from app.repositories import inventory as inventory_repo

# Initialize inventory for existing products if missing
from app.repositories import products as products_repo

products = products_repo.find_all()
for p in products:
    inv = inventory_repo.find_by_product_id(p['id'])
    if not inv:
        inventory_repo.upsert_inventory(p['id'], 100)
print("Seed completed")
