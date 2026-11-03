from decimal import Decimal
from datetime import datetime, timezone
import uuid

from app.repositories import orders as orders_repo
from app.repositories import products as products_repo
from app.repositories import inventory as inventory_repo
from app.repositories import inventory_movements as movements_repo


def _get_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _consolidate_items(items):
    consolidated = {}
    for item in items:
        pid = item.product_id
        qty = item.quantity
        if qty <= 0:
            raise ValueError("INVALID_QUANTITY")
        consolidated[pid] = consolidated.get(pid, 0) + qty
    return consolidated


def create_order(order_in, idempotency_key: str | None = None):
    # idempotency simple in-memory style persisted via order number? For V1 keep simple but follow structure
    items_consolidated = _consolidate_items(order_in.items)
    if not items_consolidated:
        raise ValueError("EMPTY_ORDER")

    # Check all products
    order_items_details = []
    for pid, qty in items_consolidated.items():
        product = products_repo.find_by_id(pid)
        if not product:
            raise ValueError("PRODUCT_NOT_FOUND")
        if not product.get('is_active', True):
            raise ValueError("PRODUCT_INACTIVE")
        inv = inventory_repo.find_by_product_id(pid)
        available = inv.get('quantity_on_hand', 0) if inv else 0
        if available < qty:
            raise ValueError("INSUFFICIENT_STOCK")
        unit_price = Decimal(str(product['unit_price']))
        line_total = unit_price * qty
        order_items_details.append({
            "product_id": pid,
            "product_name": product['name'],
            "quantity": qty,
            "unit_price": float(unit_price) if not isinstance(unit_price, float) else unit_price,
            "line_total": float(line_total),
            "_unit_price_decimal": unit_price,
        })

    total_amount = sum(Decimal(str(x['line_total'])) for x in order_items_details)

    # Create order
    order_number = f"ORD-{uuid.uuid4().hex[:12].upper()}"
    order = {
        "order_number": order_number,
        "customer_reference": order_in.customer_reference,
        "status": "CONFIRMED",
        "total_amount": float(total_amount),
        "items": [],
    }
    # build items
    for od in order_items_details:
        order["items"].append({
            "product_id": od["product_id"],
            "product_name": od["product_name"],
            "quantity": od["quantity"],
            "unit_price": od["unit_price"],
            "line_total": od["line_total"],
        })
    created = orders_repo.add_order(order)
    # deduct stock and record movements
    for od in order_items_details:
        inventory_repo.adjust_inventory(od["product_id"], -od["quantity"])
        movements_repo.add_movement(od["product_id"], "out", -od["quantity"], "order_created", order_id=created['id'])
    return created


def list_orders(status_filter: str | None = None):
    orders = orders_repo.find_all()
    if status_filter:
        orders = [o for o in orders if o.get('status') == status_filter]
    return orders


def get_order(order_id: int):
    order = orders_repo.find_by_id(order_id)
    if not order:
        raise ValueError("ORDER_NOT_FOUND")
    return order


def cancel_order(order_id: int):
    order = orders_repo.find_by_id(order_id)
    if not order:
        raise ValueError("ORDER_NOT_FOUND")
    if order.get('status') == "CANCELLED":
        raise ValueError("ALREADY_CANCELLED")
    if order.get('status') not in ("CONFIRMED", "PENDING"):
        raise ValueError("NOT_ELIGIBLE")
    # return stock
    items = order.get('items', [])
    for item in items:
        pid = item['product_id']
        qty = item['quantity']
        inventory_repo.adjust_inventory(pid, qty)
        movements_repo.add_movement(pid, "in", qty, "order_cancelled", order_id=order_id)
    updated = orders_repo.update_order(order_id, {"status": "CANCELLED"})
    return updated
