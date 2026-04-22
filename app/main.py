from fastapi import FastAPI

from app.api.v1.db_check import router as db_check_router
from app.api.v1.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)
app.include_router(db_check_router)


@app.get("/")
def root():
    return {
        "message": settings.app_name,
        "environment": settings.app_env,
    }