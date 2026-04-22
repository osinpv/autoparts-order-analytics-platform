from fastapi import APIRouter

from app.core.db import check_db_connection

router = APIRouter()


@router.get("/db-check")
def db_check():
    return check_db_connection()