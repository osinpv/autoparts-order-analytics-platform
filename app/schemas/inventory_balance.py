from datetime import datetime

from pydantic import BaseModel


class InventoryBalanceCreate(BaseModel):
    warehouse_id: int
    product_id: int
    on_hand_qty: int
    reserved_qty: int = 0


class InventoryBalanceRead(BaseModel):
    inventory_balance_id: int
    warehouse_id: int
    product_id: int
    on_hand_qty: int
    reserved_qty: int
    available_qty: int
    created_datetime: datetime
    updated_datetime: datetime