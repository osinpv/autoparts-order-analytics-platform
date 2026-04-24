from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class ProductCreate(BaseModel):
    sku: str
    product_name: str
    category_id: int | None = None
    brand_id: int | None = None
    price: Decimal
    is_active: bool = True


class ProductRead(BaseModel):
    product_id: int
    sku: str
    product_name: str
    category_id: int | None
    brand_id: int | None
    price: Decimal
    is_active: bool
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)