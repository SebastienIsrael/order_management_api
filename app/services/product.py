from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError, NotFoundError
from app.core.time import utc_now
from app.models.product import Product as ProductModel
from app.repositories import inventory as inventory_repo
from app.repositories import products as products_repo
from app.schemas.product import Product as ProductCreate
from app.schemas.product import ProductUpdate


def fetch_products(db: Session) -> list[ProductModel]:
    return products_repo.find_all(db)


def fetch_product(db: Session, product_id: int) -> ProductModel:
    product = products_repo.find_by_id(db, product_id)
    if product is None:
        raise NotFoundError("Product not found")
    return product


def register_product(db: Session, product_in: ProductCreate) -> ProductModel:
    if products_repo.find_by_sku(db, product_in.sku) is not None:
        raise ConflictError("SKU already exists")

    product = ProductModel(
        sku=product_in.sku,
        name=product_in.name,
        description=product_in.description,
        unit_price=product_in.unit_price,
        is_active=True,
    )

    try:
        products_repo.add(db, product)
        inventory_repo.get_or_create(db, product.id, initial_quantity=0)
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("SKU already exists") from None

    db.refresh(product)
    return product


def update_product(
    db: Session, product_id: int, product_in: ProductUpdate
) -> ProductModel:
    product = fetch_product(db, product_id)
    updates = product_in.model_dump(exclude_unset=True)

    # Required columns must not receive an explicit null.
    updates = {
        field: value
        for field, value in updates.items()
        if not (field in {"sku", "name", "unit_price", "is_active"} and value is None)
    }
    if not updates:
        return product

    if "sku" in updates:
        existing = products_repo.find_by_sku(db, updates["sku"])
        if existing is not None and existing.id != product_id:
            raise ConflictError("SKU already exists")

    for field, value in updates.items():
        setattr(product, field, value)
    product.updated_at = utc_now()

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ConflictError("SKU already exists") from None

    db.refresh(product)
    return product


def toggle_status(db: Session, product_id: int) -> ProductModel:
    product = fetch_product(db, product_id)
    product.is_active = not product.is_active
    product.updated_at = utc_now()
    db.commit()
    db.refresh(product)
    return product
