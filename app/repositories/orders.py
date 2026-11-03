from pathlib import Path
import json
import os
import tempfile
import copy
from datetime import datetime, timezone


file_path = Path(__file__).resolve().parent.parent / "db" / "orders_db.json"
_orders = None


def _get_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _load() -> list[dict]:
    global _orders
    if _orders is None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                json_content = f.read()
                _orders = json.loads(json_content) if json_content.strip() else []
        except FileNotFoundError:
            _orders = []
    return _orders


def _save() -> None:
    global _orders
    dir_name = os.path.dirname(file_path) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(_orders, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def find_all() -> list[dict]:
    return copy.deepcopy(_load())


def find_by_id(order_id: int) -> dict | None:
    _load()
    for o in _orders:
        if o.get('id') == order_id:
            return copy.deepcopy(o)
    return None


def find_by_order_number(order_number: str) -> dict | None:
    _load()
    for o in _orders:
        if o.get('order_number') == order_number:
            return copy.deepcopy(o)
    return None


def add_order(order: dict) -> dict:
    global _orders
    _load()
    order_id = max([o.get('id', 0) for o in _orders], default=0) + 1
    order['id'] = order_id
    if 'created_at' not in order:
        order['created_at'] = _get_utc_now()
    order['updated_at'] = _get_utc_now()
    _orders.append(order)
    _save()
    return copy.deepcopy(order)


def update_order(order_id: int, updates: dict) -> dict | None:
    global _orders
    _load()
    for o in _orders:
        if o.get('id') == order_id:
            o.update(updates)
            o['updated_at'] = _get_utc_now()
            _save()
            return copy.deepcopy(o)
    return None
