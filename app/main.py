from fastapi import FastAPI

from app.api.v1.health import router as health_router
from app.core.config import settings

app = FastAPI(title=settings.app_name)

app.include_router(health_router)


@app.get("/")
def root():
    return {
        "message": settings.app_name,
        "environment": settings.app_env,
    }