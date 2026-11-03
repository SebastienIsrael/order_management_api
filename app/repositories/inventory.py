from pathlib import Path
import json
import os
import tempfile
import copy


file_path = Path(__file__).resolve().parent.parent / "db" / "inventory_db.json"
_inventory = None


def _load() -> list[dict]:
    global _inventory
    if _inventory is None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                json_content = f.read()
                _inventory = json.loads(json_content) if json_content.strip() else []
        except FileNotFoundError:
            _inventory = []
    return _inventory


def _save() -> None:
    global _inventory
    dir_name = os.path.dirname(file_path) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(_inventory, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def find_all() -> list[dict]:
    return copy.deepcopy(_load())


def find_by_product_id(product_id: int) -> dict | None:
    _load()
    for item in _inventory:
        if item.get('product_id') == product_id:
            return copy.deepcopy(item)
    return None


def upsert_inventory(product_id: int, quantity_on_hand: int) -> dict:
    global _inventory
    _load()
    for item in _inventory:
        if item.get('product_id') == product_id:
            item['quantity_on_hand'] = quantity_on_hand
            _save()
            return copy.deepcopy(item)
    new_item = {"product_id": product_id, "quantity_on_hand": quantity_on_hand}
    _inventory.append(new_item)
    _save()
    return copy.deepcopy(new_item)


def adjust_inventory(product_id: int, delta: int) -> dict:
    global _inventory
    _load()
    for item in _inventory:
        if item.get('product_id') == product_id:
            new_qty = item['quantity_on_hand'] + delta
            if new_qty < 0:
                raise ValueError("INSUFFICIENT_STOCK")
            item['quantity_on_hand'] = new_qty
            _save()
            return copy.deepcopy(item)
    # if not exists, treat as 0
    new_qty = 0 + delta
    if new_qty < 0:
        raise ValueError("INSUFFICIENT_STOCK")
    new_item = {"product_id": product_id, "quantity_on_hand": new_qty}
    _inventory.append(new_item)
    _save()
    return copy.deepcopy(new_item)
