from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.warehouse import Warehouse
from app.schemas.inventory_movement import (
    InventoryMovementDetailsRead,
    InventoryMovementRead,
)
from app.services.inventory_service import (
    to_inventory_movement_details_read,
    to_inventory_movement_read
)

router = APIRouter(tags=["inventory-movements"])




def get_inventory_movement_or_404(
    inventory_movement_id: int,
    db: Session,
) -> InventoryMovement:
    movement = db.get(InventoryMovement, inventory_movement_id)
    if movement is None:
        raise HTTPException(status_code=404, detail="Inventory movement not found.")
    return movement


@router.get("/inventory-movements", response_model=list[InventoryMovementRead])
def get_inventory_movements(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    warehouse_code: str | None = None,
    sku: str | None = None,
    movement_type: str | None = None,
    reference_type: str | None = None,
    reference_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(InventoryMovement)
        .join(Warehouse, InventoryMovement.warehouse_id == Warehouse.warehouse_id)
        .join(Product, InventoryMovement.product_id == Product.product_id)
    )

    if warehouse_id is not None:
        stmt = stmt.where(InventoryMovement.warehouse_id == warehouse_id)

    if product_id is not None:
        stmt = stmt.where(InventoryMovement.product_id == product_id)

    if warehouse_code is not None:
        stmt = stmt.where(Warehouse.warehouse_code == warehouse_code)

    if sku is not None:
        stmt = stmt.where(Product.sku == sku)

    if movement_type is not None:
        stmt = stmt.where(InventoryMovement.movement_type == movement_type)

    if reference_type is not None:
        stmt = stmt.where(InventoryMovement.reference_type == reference_type)

    if reference_id is not None:
        stmt = stmt.where(InventoryMovement.reference_id == reference_id)

    stmt = stmt.order_by(InventoryMovement.inventory_movement_id)

    movements = db.execute(stmt).scalars().all()
    return [to_inventory_movement_read(movement) for movement in movements]


@router.get(
    "/inventory-movements/details",
    response_model=list[InventoryMovementDetailsRead],
)
def get_inventory_movement_details(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    warehouse_code: str | None = None,
    sku: str | None = None,
    movement_type: str | None = None,
    reference_type: str | None = None,
    reference_id: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(InventoryMovement, Warehouse, Product)
        .join(Warehouse, InventoryMovement.warehouse_id == Warehouse.warehouse_id)
        .join(Product, InventoryMovement.product_id == Product.product_id)
    )

    if warehouse_id is not None:
        stmt = stmt.where(InventoryMovement.warehouse_id == warehouse_id)

    if product_id is not None:
        stmt = stmt.where(InventoryMovement.product_id == product_id)

    if warehouse_code is not None:
        stmt = stmt.where(Warehouse.warehouse_code == warehouse_code)

    if sku is not None:
        stmt = stmt.where(Product.sku == sku)

    if movement_type is not None:
        stmt = stmt.where(InventoryMovement.movement_type == movement_type)

    if reference_type is not None:
        stmt = stmt.where(InventoryMovement.reference_type == reference_type)

    if reference_id is not None:
        stmt = stmt.where(InventoryMovement.reference_id == reference_id)

    stmt = stmt.order_by(InventoryMovement.inventory_movement_id)

    rows = db.execute(stmt).all()

    return [
        to_inventory_movement_details_read(
            movement=movement,
            warehouse=warehouse,
            product=product,
        )
        for movement, warehouse, product in rows
    ]


@router.get(
    "/inventory-movements/{inventory_movement_id}",
    response_model=InventoryMovementRead,
)
def get_inventory_movement(
    inventory_movement_id: int,
    db: Session = Depends(get_db),
):
    movement = get_inventory_movement_or_404(inventory_movement_id, db)
    return to_inventory_movement_read(movement)
