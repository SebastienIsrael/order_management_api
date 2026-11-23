from decimal import Decimal

from app.core.enums import MovementType
from app.db.session import SessionLocal
from app.repositories import products as products_repo
from app.schemas.inventory import MovementCreate
from app.schemas.product import Product as ProductCreate
from app.services import inventory as inventory_service
from app.services import product as product_service

SEED_PRODUCTS = [
    {
        "sku": "GPU-0001",
        "name": "NVIDIA GeForce RTX 5090 Ti 32GB GDDR7",
        "description": "Placa de video topo de linha com 32GB GDDR7",
        "unit_price": Decimal("12999.90"),
    },
    {
        "sku": "CPU-0002",
        "name": "Intel Core i9-15900KX 24C/32T 6.2GHz",
        "description": "Processador desktop de 24 nucleos com boost de 6.2GHz",
        "unit_price": Decimal("8499.90"),
    },
    {
        "sku": "RAM-0003",
        "name": "Memoria DDR5 32GB 6000MHz",
        "description": "Kit de memoria de alto desempenho",
        "unit_price": Decimal("899.90"),
    },
]


def main() -> None:
    with SessionLocal() as db:
        if products_repo.find_all(db):
            print("Seed skipped: products already exist.")
            return

        for product_data in SEED_PRODUCTS:
            product = product_service.register_product(
                db, ProductCreate(**product_data)
            )
            inventory_service.add_movement(
                db,
                product.id,
                MovementCreate(
                    quantity=100,
                    movement_type=MovementType.IN,
                    reason="seed",
                ),
            )
            print(f"Created product {product.sku} with 100 units.")

    print("Seed completed.")


if __name__ == "__main__":
    main()
