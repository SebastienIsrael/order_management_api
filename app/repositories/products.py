from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product


def find_all(db: Session) -> list[Product]:
    return list(db.scalars(select(Product).order_by(Product.id)).all())


def find_by_id(db: Session, product_id: int) -> Product | None:
    return db.get(Product, product_id)


def find_by_sku(db: Session, sku: str) -> Product | None:
    return db.scalar(select(Product).where(Product.sku == sku))


def add(db: Session, product: Product) -> Product:
    db.add(product)
    db.flush()
    return product
