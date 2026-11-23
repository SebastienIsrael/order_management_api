# AGENTS.md

## What this is
FastAPI order/inventory API with a layered flow:
`app/api/v1/endpoints/*` -> `app/services/*` -> `app/repositories/*` -> SQLAlchemy models -> SQL database.
The default database is SQLite (`sqlite:///./order_management.db`); PostgreSQL is supported through
`DATABASE_URL`. The legacy `app/db/*_db.json` files are import-only data and are not read at runtime.

## Commands
- `uv sync` — install/refresh deps. Python >=3.14 is required.
- `uv run python -m alembic upgrade head` — create/update the schema. Use `python -m alembic`, not the
  bare `alembic` command: on this Windows machine the console script is blocked by Application Control.
- `uv run python scripts/import_json.py` — import the legacy JSON dataset (idempotent by primary key).
- `uv run python scripts/seed.py` — create a small demo catalog if no products exist.
- `uv run pytest` — test suite. Single test: `uv run pytest tests/api/test_orders.py::test_name -q`.
- `uv run fastapi dev` — dev server (or `uv run uvicorn app.main:app --reload`; `[tool.fastapi]` sets the entrypoint).

## Transaction and session rules
- Endpoints obtain `Session` via `Depends(get_db)` from `app/db/session.py`.
- Services own the transaction boundary: they call `db.commit()` on success and `db.rollback()` on failure.
- Repositories never commit. They may `db.flush()` to obtain generated IDs.
- `SessionLocal` uses `expire_on_commit=False`; response serialization can read ORM objects after commit.
- Order creation and cancellation must remain single transactions. Do not commit inside repository helpers.
- Stock changes use conditional SQL updates (`inventory_repo.try_decrement` / `increment`) so concurrent
  requests cannot oversell. Keep that behavior when touching order or inventory code.

## Error handling
- Services raise `NotFoundError`, `ConflictError`, `BadRequestError` or `UnprocessableEntityError`
  from `app/core/exceptions.py`. `app/main.py` registers the global handler.
- Do not reintroduce `ValueError("SOME_CODE")` + per-endpoint string mapping. It was removed intentionally.
- Unexpected exceptions should surface as 500; endpoints no longer swallow every exception.

## Data and contracts
- ORM models live in `app/models/`; Pydantic API models live in `app/schemas/`; they are different types.
- Money is `Decimal` end to end and stored as `Numeric(12,2)` / `Numeric(14,2)`. Never cast prices to float.
- Timestamps are timezone-aware `datetime` values from `app/core/time.py`.
- Enum values live in `app/core/enums.py` (`OrderStatus`, `MovementType`). Changing them requires a migration.
- Collection routes are registered twice (`""` and `"/"`) to avoid 307 redirects; keep that pattern.
- Path params are standardized as `product_id` and `order_id`.

## Database workflow
- After changing models: `uv run python -m alembic revision --autogenerate -m "..."`, review the generated
  file, then `uv run python -m alembic upgrade head`.
- Do not edit an applied migration; add a new revision.
- Do not commit `.env`, `*.db` or `*.sqlite3` (already ignored).
- `scripts/import_json.py` preserves legacy IDs and resets PostgreSQL sequences after import.

## Tests
- `tests/conftest.py` creates a fresh in-memory SQLite database per test and overrides `get_db`.
- API tests use `TestClient`; the same session is shared by the fixture, so service commits are visible.
- When adding a table/model, import it in `app/models/__init__.py` so Alembic autogenerate sees it.
