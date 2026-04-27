from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class PaymentCreate(BaseModel):
    payment_method: str


class PaymentRead(BaseModel):
    payment_id: int
    payment_number: str
    order_id: int
    payment_status: str
    payment_method: str
    amount: Decimal
    paid_datetime: datetime | None
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)