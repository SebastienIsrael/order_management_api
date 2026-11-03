# Order Management API

## Problem statement
Small electronics store needs order processing and inventory management.

## Features (V1 - In-memory prototype)
- Product catalog (create, list, get, update, toggle status)
- Inventory management with movements
- Order creation with multiple items, price calculation on server
- Consolidation of duplicate products in order
- Reject orders with insufficient stock (no partial fulfillment)
- Cancel eligible orders with stock return
- Basic validation and error handling

## Tech stack
- Python 3.13, FastAPI, Pydantic, Uvicorn
- In-memory JSON storage (V1)

## Structure
See code layout under app/

## Running
```bash
pip install -e .
uvicorn app.main:app --reload
```

## API docs
Available at /docs

## Limitations (V1)
- Data stored in JSON files, not persistent across different storage backends as required for V2
- Idempotency/basic concurrency protections limited in pure in-memory approach
- No auth/authorization
- Tests not yet comprehensive
