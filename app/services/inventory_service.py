from sqlalchemy import select, text
from sqlalchemy.exc import DBAPIError
from sqlalchemy.orm import Session

from fastapi import HTTPException

from app.models.inventory_balance import InventoryBalance
from app.models.inventory_movement import InventoryMovement


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


def get_inventory_balance_for_update_by_business_key_or_404(
    *,
    warehouse_id: int,
    product_id: int,
    db: Session,
) -> InventoryBalance:
    db.execute(text("SET LOCAL lock_timeout = '15s'"))

    stmt = (
        select(InventoryBalance)
        .where(InventoryBalance.warehouse_id == warehouse_id)
        .where(InventoryBalance.product_id == product_id)
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
        raise HTTPException(
            status_code=404,
            detail=f"Inventory balance not found for warehouse_id={warehouse_id}, product_id={product_id}.",
        )

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


def reserve_inventory_balance(
    *,
    balance: InventoryBalance,
    qty: int,
    db: Session,
    movement_type: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
    comment_text: str | None = None,
) -> None:
    available_qty = balance.on_hand_qty - balance.reserved_qty

    if available_qty < qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Not enough available inventory. "
                f"Requested={qty}, available={available_qty}."
            ),
        )

    balance.reserved_qty += qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=movement_type,
        qty=qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=reference_type,
        reference_id=reference_id,
        comment_text=comment_text,
    )


def release_inventory_balance(
    *,
    balance: InventoryBalance,
    qty: int,
    db: Session,
    movement_type: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
    comment_text: str | None = None,
) -> None:
    if balance.reserved_qty < qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot release more than currently reserved. "
                f"Requested={qty}, reserved={balance.reserved_qty}."
            ),
        )

    balance.reserved_qty -= qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=movement_type,
        qty=qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=reference_type,
        reference_id=reference_id,
        comment_text=comment_text,
    )


def receive_inventory_balance(
    *,
    balance: InventoryBalance,
    qty: int,
    db: Session,
    movement_type: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
    comment_text: str | None = None,
) -> None:
    balance.on_hand_qty += qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=movement_type,
        qty=qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=reference_type,
        reference_id=reference_id,
        comment_text=comment_text,
    )


def ship_inventory_balance(
    *,
    balance: InventoryBalance,
    qty: int,
    db: Session,
    movement_type: str,
    reference_type: str | None = None,
    reference_id: int | None = None,
    comment_text: str | None = None,
) -> None:
    if balance.reserved_qty < qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot ship more than currently reserved. "
                f"Requested={qty}, reserved={balance.reserved_qty}."
            ),
        )

    if balance.on_hand_qty < qty:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot ship more than currently on hand. "
                f"Requested={qty}, on_hand={balance.on_hand_qty}."
            ),
        )

    balance.on_hand_qty -= qty
    balance.reserved_qty -= qty

    add_inventory_movement(
        db=db,
        warehouse_id=balance.warehouse_id,
        product_id=balance.product_id,
        movement_type=movement_type,
        qty=qty,
        resulting_on_hand_qty=balance.on_hand_qty,
        resulting_reserved_qty=balance.reserved_qty,
        reference_type=reference_type,
        reference_id=reference_id,
        comment_text=comment_text,
    )