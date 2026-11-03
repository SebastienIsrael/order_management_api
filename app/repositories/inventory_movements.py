from pathlib import Path
import json
import os
import tempfile
import copy
from datetime import datetime, timezone


file_path = Path(__file__).resolve().parent.parent / "db" / "inventory_movements_db.json"
_movements = None


def _get_utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')


def _load() -> list[dict]:
    global _movements
    if _movements is None:
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                json_content = f.read()
                _movements = json.loads(json_content) if json_content.strip() else []
        except FileNotFoundError:
            _movements = []
    return _movements


def _save() -> None:
    global _movements
    dir_name = os.path.dirname(file_path) or '.'
    fd, tmp_path = tempfile.mkstemp(dir=dir_name, suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(_movements, f, indent=4, ensure_ascii=False)
        os.replace(tmp_path, file_path)
    except Exception:
        try:
            os.unlink(tmp_path)
        except Exception:
            pass
        raise


def add_movement(product_id: int, movement_type: str, quantity_delta: int, reason: str, order_id: int | None = None) -> dict:
    global _movements
    _load()
    movement_id = max([m.get('id', 0) for m in _movements], default=0) + 1
    movement = {
        "id": movement_id,
        "product_id": product_id,
        "order_id": order_id,
        "movement_type": movement_type,
        "quantity_delta": quantity_delta,
        "reason": reason,
        "created_at": _get_utc_now(),
    }
    _movements.append(movement)
    _save()
    return copy.deepcopy(movement)


def find_by_product_id(product_id: int) -> list[dict]:
    _load()
    result = [m for m in _movements if m.get('product_id') == product_id]
    return copy.deepcopy(result)
