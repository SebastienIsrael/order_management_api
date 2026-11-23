"""Import the legacy JSON files from V1 into the relational database.

The import is idempotent: rows already present by primary key are skipped.
Run after `alembic upgrade head`:

    uv run python scripts/import_json.py
"""

import argparse
import json
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from sqlalchemy import select, text

from app.core.enums import MovementType, OrderStatus
from app.core.time import utc_now
from app.db.session import SessionLocal
from app.models.inventory import Inventory
from app.models.inventory_movement import InventoryMovement
from app.models.order import Order, OrderItem
from app.models.product import Product


def parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_json(path: Path) -> list[dict]:
    if not path.exists():
        return []
    content = path.read_text(encoding="utf-8-sig").strip()
    return json.loads(content) if content else []


def import_products(db, rows: list[dict]) -> int:
    imported = 0
    for row in rows:
        if db.get(Product, row["id"]) is not None:
            continue
        if db.scalar(select(Product).where(Product.sku == row["sku"])) is not None:
            continue

        db.add(
            Product(
                id=row["id"],
                sku=row["sku"],
                name=row["name"],
                description=row.get("description"),
                unit_price=Decimal(str(row["unit_price"])),
                is_active=row.get("is_active", True),
                created_at=parse_datetime(row.get("created_at")) or utc_now(),
                updated_at=parse_datetime(row.get("updated_at")),
            )
        )
        imported += 1
    db.flush()
    return imported


def import_inventory(db, rows: list[dict]) -> int:
    imported = 0
    for row in rows:
        product_id = row["product_id"]
        if db.get(Inventory, product_id) is not None:
            continue
        if db.get(Product, product_id) is None:
            continue

        db.add(
            Inventory(
                product_id=product_id,
                quantity_on_hand=row.get("quantity_on_hand", 0),
            )
        )
        imported += 1
    db.flush()
    return imported


def import_orders(db, rows: list[dict]) -> int:
    imported = 0
    for row in rows:
        order_id = row["id"]
        if db.get(Order, order_id) is not None:
            continue
        if (
            db.scalar(select(Order).where(Order.order_number == row["order_number"]))
            is not None
        ):
            continue

        created_at = parse_datetime(row.get("created_at")) or utc_now()
        order = Order(
            id=order_id,
            order_number=row["order_number"],
            customer_reference=row["customer_reference"],
            status=OrderStatus(row.get("status", OrderStatus.CONFIRMED.value)),
            total_amount=Decimal(str(row.get("total_amount", 0))),
            created_at=created_at,
            updated_at=parse_datetime(row.get("updated_at")) or created_at,
        )
        db.add(order)
        db.flush()

        for item in row.get("items", []):
            db.add(
                OrderItem(
                    order_id=order_id,
                    product_id=item["product_id"],
                    product_name=item["product_name"],
                    quantity=item["quantity"],
                    unit_price=Decimal(str(item["unit_price"])),
                    line_total=Decimal(str(item["line_total"])),
                )
            )
        imported += 1
    db.flush()
    return imported


def import_movements(db, rows: list[dict]) -> int:
    imported = 0
    for row in rows:
        movement_id = row["id"]
        if db.get(InventoryMovement, movement_id) is not None:
            continue

        db.add(
            InventoryMovement(
                id=movement_id,
                product_id=row["product_id"],
                order_id=row.get("order_id"),
                movement_type=MovementType(row["movement_type"]),
                quantity_delta=row["quantity_delta"],
                reason=row["reason"],
                created_at=parse_datetime(row.get("created_at")) or utc_now(),
            )
        )
        imported += 1
    db.flush()
    return imported


def reset_postgres_sequences(db) -> None:
    if db.bind is None or db.bind.dialect.name != "postgresql":
        return

    for table in ("products", "orders", "order_items", "inventory_movements"):
        db.execute(
            text(
                f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
            )
        )
    db.commit()


def main() -> None:
    parser = argparse.ArgumentParser(description="Import legacy JSON data into the database.")
    parser.add_argument(
        "--json-dir",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "app" / "db",
    )
    args = parser.parse_args()

    with SessionLocal() as db:
        products = import_products(db, read_json(args.json_dir / "products_db.json"))
        inventory = import_inventory(db, read_json(args.json_dir / "inventory_db.json"))
        orders = import_orders(db, read_json(args.json_dir / "orders_db.json"))
        movements = import_movements(
            db, read_json(args.json_dir / "inventory_movements_db.json")
        )
        db.commit()
        reset_postgres_sequences(db)

    print(
        "Import completed: "
        f"{products} products, {inventory} inventory rows, "
        f"{orders} orders, {movements} movements."
    )


if __name__ == "__main__":
    main()
