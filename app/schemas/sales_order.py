from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class SalesOrderItemCreate(BaseModel):
    product_id: int
    warehouse_id: int
    qty: int = Field(..., gt=0)


class SalesOrderCreate(BaseModel):
    order_number: str
    customer_email: EmailStr
    items: list[SalesOrderItemCreate] = Field(..., min_length=1)


class SalesOrderItemRead(BaseModel):
    order_item_id: int
    order_id: int
    product_id: int
    warehouse_id: int
    qty: int
    unit_price: Decimal
    line_amount: Decimal
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderRead(BaseModel):
    order_id: int
    order_number: str
    customer_email: EmailStr
    order_status: str
    order_total_amount: Decimal
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)


class SalesOrderDetailsRead(BaseModel):
    order_id: int
    order_number: str
    customer_email: EmailStr
    order_status: str
    order_total_amount: Decimal
    created_datetime: datetime
    updated_datetime: datetime
    items: list[SalesOrderItemRead]