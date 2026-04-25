from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError, IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.enums import InventoryMovementType, InventoryReferenceType
from app.models.inventory_balance import InventoryBalance
from app.models.inventory_movement import InventoryMovement
from app.models.product import Product
from app.models.product_brand import ProductBrand
from app.models.product_category import ProductCategory
from app.models.warehouse import Warehouse
from app.schemas.inventory_balance import (
    InventoryBalanceCreate,
    InventoryBalanceDetailsRead,
    InventoryBalanceQuantityOperation,
    InventoryBalanceRead,
)

router = APIRouter(tags=["inventory-balances"])


def to_inventory_balance_read(balance: InventoryBalance) -> InventoryBalanceRead:
    return InventoryBalanceRead(
        inventory_balance_id=balance.inventory_balance_id,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        on_hand_qty=balance.on_hand_qty,
        reserved_qty=balance.reserved_qty,
        available_qty=balance.on_hand_qty - balance.reserved_qty,
        created_datetime=balance.created_datetime,
        updated_datetime=balance.updated_datetime,
    )


def to_inventory_balance_details_read(
    balance: InventoryBalance,
    warehouse: Warehouse,
    product: Product,
    category: ProductCategory | None,
    brand: ProductBrand | None,
) -> InventoryBalanceDetailsRead:
    return InventoryBalanceDetailsRead(
        inventory_balance_id=balance.inventory_balance_id,
        warehouse_id=warehouse.warehouse_id,
        warehouse_code=warehouse.warehouse_code,
        warehouse_name=warehouse.warehouse_name,
        product_id=product.product_id,
        sku=product.sku,
        product_name=product.product_name,
        category_id=product.category_id,
        category_name=category.category_name if category else None,
        brand_id=product.brand_id,
        brand_name=brand.brand_name if brand else None,
        on_hand_qty=balance.on_hand_qty,
        reserved_qty=balance.reserved_qty,
        available_qty=balance.on_hand_qty - balance.reserved_qty,
        created_datetime=balance.created_datetime,
        updated_datetime=balance.updated_datetime,
    )


def get_inventory_balance_or_404(
    inventory_balance_id: int,
    db: Session,
) -> InventoryBalance:
    balance = db.get(InventoryBalance, inventory_balance_id)
    if balance is None:
        raise HTTPException(status_code=404, detail="Inventory balance not found.")
    return balance


def get_inventory_balance_for_update_or_404(
    inventory_balance_id: int,
    db: Session,
) -> InventoryBalance:
    db.execute(text("SET LOCAL lock_timeout = '15s'"))

    stmt = (
        select(InventoryBalance)
        .where(InventoryBalance.inventory_balance_id == inventory_balance_id)
        .with_for_update()
    )

    try:
        balance = db.execute(stmt).scalar_one_or_none()
    except DBAPIError as exc:
        db.rollback()

        error_text = str(exc.orig).lower() if exc.orig else str(exc).lower()

        if "lock timeout" in error_text:
            raise HTTPException(
                status_code=409,
                detail="Resource busy, try again later.",
            ) from exc

        raise

    if balance is None:
        raise HTTPException(status_code=404, detail="Inventory balance not found.")

    return balance


def add_inventory_movement(
    *,
    db: Session,
    warehouse_id: int,
    product_id: int,
    movement_type: str,
    qty: int,
    resulting_on_hand_qty: int,
    resulting_reserved_qty: int,
    reference_type: str | None = None,
    reference_id: int | None = None,
    comment_text: str | None = None,
) -> None:
    movement = InventoryMovement(
        warehouse_id=warehouse_id,
        product_id=product_id,
        movement_type=movement_type,
        qty=qty,
        resulting_on_hand_qty=resulting_on_hand_qty,
        resulting_reserved_qty=resulting_reserved_qty,
        reference_type=reference_type,
        reference_id=reference_id,
        comment_text=comment_text,
    )
    db.add(movement)


@router.post("/inventory-balances", response_model=InventoryBalanceRead)
def create_inventory_balance(
    payload: InventoryBalanceCreate,
    db: Session = Depends(get_db),
):
    balance = InventoryBalance(
        warehouse_id=payload.warehouse_id,
        product_id=payload.product_id,
        on_hand_qty=payload.on_hand_qty,
        reserved_qty=payload.reserved_qty,
    )
    db.add(balance)

    add_inventory_movement(
        db=db,
        warehouse_id=payload.warehouse_id,
        product_id=payload.product_id,
        movement_type=InventoryMovementType.INITIAL_LOAD.value,
        qty=payload.on_hand_qty,
        resulting_on_hand_qty=payload.on_hand_qty,
        resulting_reserved_qty=payload.reserved_qty,
        reference_type=InventoryReferenceType.INVENTORY_BALANCE.value,
        comment_text="Initial inventory balance creation.",
    )

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)


@router.get("/inventory-balances", response_model=list[InventoryBalanceRead])
def get_inventory_balances(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    warehouse_code: str | None = None,
    sku: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    category_name: str | None = None,
    brand_name: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(InventoryBalance)
        .join(Warehouse, InventoryBalance.warehouse_id == Warehouse.warehouse_id)
        .join(Product, InventoryBalance.product_id == Product.product_id)
        .join(
            ProductCategory,
            Product.category_id == ProductCategory.category_id,
            isouter=True,
        )
        .join(
            ProductBrand,
            Product.brand_id == ProductBrand.brand_id,
            isouter=True,
        )
    )

    if warehouse_id is not None:
        stmt = stmt.where(InventoryBalance.warehouse_id == warehouse_id)

    if product_id is not None:
        stmt = stmt.where(InventoryBalance.product_id == product_id)

    if warehouse_code is not None:
        stmt = stmt.where(Warehouse.warehouse_code == warehouse_code)

    if sku is not None:
        stmt = stmt.where(Product.sku == sku)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    if brand_id is not None:
        stmt = stmt.where(Product.brand_id == brand_id)

    if category_name is not None:
        stmt = stmt.where(ProductCategory.category_name == category_name)

    if brand_name is not None:
        stmt = stmt.where(ProductBrand.brand_name == brand_name)

    stmt = stmt.order_by(InventoryBalance.inventory_balance_id)

    balances = db.execute(stmt).scalars().all()
    return [to_inventory_balance_read(balance) for balance in balances]


@router.get(
    "/inventory-balances/details",
    response_model=list[InventoryBalanceDetailsRead],
)
def get_inventory_balance_details(
    warehouse_id: int | None = None,
    product_id: int | None = None,
    warehouse_code: str | None = None,
    sku: str | None = None,
    category_id: int | None = None,
    brand_id: int | None = None,
    category_name: str | None = None,
    brand_name: str | None = None,
    db: Session = Depends(get_db),
):
    stmt = (
        select(
            InventoryBalance,
            Warehouse,
            Product,
            ProductCategory,
            ProductBrand,
        )
        .join(Warehouse, InventoryBalance.warehouse_id == Warehouse.warehouse_id)
        .join(Product, InventoryBalance.product_id == Product.product_id)
        .join(
            ProductCategory,
            Product.category_id == ProductCategory.category_id,
            isouter=True,
        )
        .join(
            ProductBrand,
            Product.brand_id == ProductBrand.brand_id,
            isouter=True,
        )
    )

    if warehouse_id is not None:
        stmt = stmt.where(InventoryBalance.warehouse_id == warehouse_id)

    if product_id is not None:
        stmt = stmt.where(InventoryBalance.product_id == product_id)

    if warehouse_code is not None:
        stmt = stmt.where(Warehouse.warehouse_code == warehouse_code)

    if sku is not None:
        stmt = stmt.where(Product.sku == sku)

    if category_id is not None:
        stmt = stmt.where(Product.category_id == category_id)

    if brand_id is not None:
        stmt = stmt.where(Product.brand_id == brand_id)

    if category_name is not None:
        stmt = stmt.where(ProductCategory.category_name == category_name)

    if brand_name is not None:
        stmt = stmt.where(ProductBrand.brand_name == brand_name)

    stmt = stmt.order_by(InventoryBalance.inventory_balance_id)

    rows = db.execute(stmt).all()

    return [
        to_inventory_balance_details_read(
            balance=balance,
            warehouse=warehouse,
            product=product,
            category=category,
            brand=brand,
        )
        for balance, warehouse, product, category, brand in rows
    ]


@router.get(
    "/inventory-balances/{inventory_balance_id}",
    response_model=InventoryBalanceRead,
)
def get_inventory_balance(
    inventory_balance_id: int,
    db: Session = Depends(get_db),
):
    balance = get_inventory_balance_or_404(inventory_balance_id, db)
    return to_inventory_balance_read(balance)


@router.post(
    "/inventory-balances/{inventory_balance_id}/reserve",
    response_model=InventoryBalanceRead,
)
def reserve_inventory(
    inventory_balance_id: int,
    payload: InventoryBalanceQuantityOperation,
    db: Session = Depends(get_db),
):
    balance = get_inventory_balance_for_update_or_404(inventory_balance_id, db)

    available_qty = balance.on_hand_qty - balance.reserved_qty
    if available_qty < payload.qty:
        raise HTTPException(
            status_code=400,
            detail="Not enough available inventory to reserve requested quantity.",
        )

    balance.reserved_qty += payload.qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=InventoryMovementType.RESERVE.value,
        qty=payload.qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=InventoryReferenceType.INVENTORY_BALANCE.value,
        reference_id=balance.inventory_balance_id,
        comment_text="Inventory reserved.",
    )

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)


@router.post(
    "/inventory-balances/{inventory_balance_id}/release",
    response_model=InventoryBalanceRead,
)
def release_inventory(
    inventory_balance_id: int,
    payload: InventoryBalanceQuantityOperation,
    db: Session = Depends(get_db),
):
    balance = get_inventory_balance_for_update_or_404(inventory_balance_id, db)

    if balance.reserved_qty < payload.qty:
        raise HTTPException(
            status_code=400,
            detail="Cannot release more than currently reserved quantity.",
        )

    balance.reserved_qty -= payload.qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=InventoryMovementType.RELEASE.value,
        qty=payload.qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=InventoryReferenceType.INVENTORY_BALANCE.value,
        reference_id=balance.inventory_balance_id,
        comment_text="Reserved inventory released.",
    )

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)


@router.post(
    "/inventory-balances/{inventory_balance_id}/receive",
    response_model=InventoryBalanceRead,
)
def receive_inventory(
    inventory_balance_id: int,
    payload: InventoryBalanceQuantityOperation,
    db: Session = Depends(get_db),
):
    balance = get_inventory_balance_for_update_or_404(inventory_balance_id, db)

    balance.on_hand_qty += payload.qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=InventoryMovementType.RECEIVE.value,
        qty=payload.qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=InventoryReferenceType.INVENTORY_BALANCE.value,
        reference_id=balance.inventory_balance_id,
        comment_text="Inventory received into stock.",
    )
        
    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)


@router.post(
    "/inventory-balances/{inventory_balance_id}/ship",
    response_model=InventoryBalanceRead,
)
def ship_inventory(
    inventory_balance_id: int,
    payload: InventoryBalanceQuantityOperation,
    db: Session = Depends(get_db),
):
    balance = get_inventory_balance_for_update_or_404(inventory_balance_id, db)

    if balance.reserved_qty < payload.qty:
        raise HTTPException(
            status_code=400,
            detail="Cannot ship more than currently reserved quantity.",
        )

    if balance.on_hand_qty < payload.qty:
        raise HTTPException(
            status_code=400,
            detail="Cannot ship more than currently available on-hand quantity.",
        )

    balance.on_hand_qty -= payload.qty
    balance.reserved_qty -= payload.qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=InventoryMovementType.SHIP.value,
        qty=payload.qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=InventoryReferenceType.INVENTORY_BALANCE.value,
        reference_id=balance.inventory_balance_id,
        comment_text="Reserved inventory shipped.",
    )
    
    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)