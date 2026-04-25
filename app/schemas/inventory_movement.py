from datetime import datetime

from pydantic import BaseModel


class InventoryMovementRead(BaseModel):
    inventory_movement_id: int
    warehouse_id: int
    product_id: int
    movement_type: str
    qty: int
    resulting_on_hand_qty: int
    resulting_reserved_qty: int
    resulting_available_qty: int
    reference_type: str | None
    reference_id: int | None
    comment_text: str | None
    created_datetime: datetime


class InventoryMovementDetailsRead(BaseModel):
    inventory_movement_id: int
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    product_id: int
    sku: str
    product_name: str
    movement_type: str
    qty: int
    resulting_on_hand_qty: int
    resulting_reserved_qty: int
    resulting_available_qty: int
    reference_type: str | None
    reference_id: int | None
    comment_text: str | None
    created_datetime: datetime