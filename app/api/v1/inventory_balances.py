from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.inventory_balance import InventoryBalance
from app.schemas.inventory_balance import InventoryBalanceCreate, InventoryBalanceRead

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

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(balance)
    return to_inventory_balance_read(balance)


@router.get("/inventory-balances", response_model=list[InventoryBalanceRead])
def get_inventory_balances(db: Session = Depends(get_db)):
    stmt = select(InventoryBalance).order_by(InventoryBalance.inventory_balance_id)
    balances = db.execute(stmt).scalars().all()
    return [to_inventory_balance_read(balance) for balance in balances]