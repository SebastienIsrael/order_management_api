from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers

app = FastAPI(
    title="Order Management API",
    description="API REST for order processing and inventory management",
    version="2.0.0",
)

register_exception_handlers(app)
app.include_router(api_router, prefix="/api/v1")
