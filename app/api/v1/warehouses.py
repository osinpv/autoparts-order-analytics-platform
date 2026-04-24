from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.warehouse import Warehouse
from app.schemas.warehouse import WarehouseCreate, WarehouseRead

router = APIRouter(tags=["warehouses"])


@router.post("/warehouses", response_model=WarehouseRead)
def create_warehouse(
    payload: WarehouseCreate,
    db: Session = Depends(get_db),
):
    warehouse = Warehouse(
        warehouse_code=payload.warehouse_code,
        warehouse_name=payload.warehouse_name,
        region=payload.region,
    )
    db.add(warehouse)

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(warehouse)
    return warehouse


@router.get("/warehouses", response_model=list[WarehouseRead])
def get_warehouses(db: Session = Depends(get_db)):
    stmt = select(Warehouse).order_by(Warehouse.warehouse_id)
    warehouses = db.execute(stmt).scalars().all()
    return warehouses