from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductBrandCreate(BaseModel):
    brand_name: str


class ProductBrandRead(BaseModel):
    brand_id: int
    brand_name: str
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)