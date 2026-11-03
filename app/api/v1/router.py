from fastapi import APIRouter

from app.api.v1.endpoints import products, inventory, orders

api_router = APIRouter()
api_router.include_router(products.router)
api_router.include_router(inventory.router)
api_router.include_router(orders.router)
