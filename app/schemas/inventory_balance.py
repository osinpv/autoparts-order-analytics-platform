from datetime import datetime

from pydantic import BaseModel, Field


class InventoryBalanceCreate(BaseModel):
    warehouse_id: int
    product_id: int
    on_hand_qty: int
    reserved_qty: int = 0


class InventoryBalanceQuantityOperation(BaseModel):
    qty: int = Field(..., gt=0)


class InventoryBalanceRead(BaseModel):
    inventory_balance_id: int
    warehouse_id: int
    product_id: int
    on_hand_qty: int
    reserved_qty: int
    available_qty: int
    created_datetime: datetime
    updated_datetime: datetime


class InventoryBalanceDetailsRead(BaseModel):
    inventory_balance_id: int
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    product_id: int
    sku: str
    product_name: str
    category_id: int | None
    category_name: str | None
    brand_id: int | None
    brand_name: str | None
    on_hand_qty: int
    reserved_qty: int
    available_qty: int
    created_datetime: datetime
    updated_datetime: datetime