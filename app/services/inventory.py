from app.repositories import inventory as inventory_repo
from app.repositories import inventory_movements as movements_repo
from app.repositories import products as products_repo


def get_inventory(product_id: int):
    product = products_repo.find_by_id(product_id)
    if not product:
        raise ValueError("PROD_NOT_FOUND")
    inv = inventory_repo.find_by_product_id(product_id)
    if not inv:
        inv = inventory_repo.upsert_inventory(product_id, 0)
    return inv


def add_movement(product_id: int, movement_in):
    product = products_repo.find_by_id(product_id)
    if not product:
        raise ValueError("PROD_NOT_FOUND")
    quantity = movement_in.quantity
    movement_type = movement_in.movement_type
    reason = movement_in.reason
    if quantity <= 0:
        raise ValueError("INVALID_QUANTITY")
    if movement_type == "in":
        result = inventory_repo.adjust_inventory(product_id, quantity)
        movements_repo.add_movement(product_id, movement_type, quantity, reason)
        return result
    elif movement_type == "out":
        result = inventory_repo.adjust_inventory(product_id, -quantity)
        movements_repo.add_movement(product_id, movement_type, -quantity, reason)
        return result
    elif movement_type == "adjustment":
        # adjustment treated as setting/addition per request? But rules say don't set arbitrary value directly except via movement
        # interpret as adding quantity if positive? or require explicit - but schema says quantity>0; we already adjust by delta
        # treat as in for simplicity
        result = inventory_repo.adjust_inventory(product_id, quantity)
        movements_repo.add_movement(product_id, movement_type, quantity, reason)
        return result
    raise ValueError("INVALID_MOVEMENT_TYPE")


def get_movements(product_id: int):
    product = products_repo.find_by_id(product_id)
    if not product:
        raise ValueError("PROD_NOT_FOUND")
    return movements_repo.find_by_product_id(product_id)
