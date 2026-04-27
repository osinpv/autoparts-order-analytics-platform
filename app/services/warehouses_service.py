from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.warehouse import Warehouse


def get_warehouse_or_404(warehouse_id: int, db: Session) -> Warehouse:
    warehouse = db.get(Warehouse, warehouse_id)
    if warehouse is None:
        raise HTTPException(status_code=404, detail="Warehouse not found.")
    return warehouse
