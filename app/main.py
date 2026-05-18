from fastapi import FastAPI

import app.models.all_models
from app.core.config import settings
from app.api.v1.brands import router as brands_router
from app.api.v1.categories import router as categories_router
from app.api.v1.db_check import router as db_check_router
from app.api.v1.health import router as health_router
from app.api.v1.inventory_balances import router as inventory_balances_router
from app.api.v1.inventory_movements import router as inventory_movements_router
from app.api.v1.products import router as products_router
from app.api.v1.warehouses import router as warehouses_router
from app.api.v1.orders import router as orders_router
from app.api.v1.shipments import router as shipments_router
from app.api.v1.payments import router as payments_router
from app.api.v1.product_documents import router as product_documents_router

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(db_check_router)
app.include_router(categories_router)
app.include_router(brands_router)
app.include_router(products_router)
app.include_router(warehouses_router)
app.include_router(inventory_balances_router)
app.include_router(inventory_movements_router)
app.include_router(orders_router)
app.include_router(shipments_router)
app.include_router(payments_router)
app.include_router(product_documents_router)

@app.get("/")
def root():
    return {
        "message": settings.app_name,
        "environment": settings.app_env,
    }