from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WarehouseCreate(BaseModel):
    warehouse_code: str
    warehouse_name: str
    region: str


class WarehouseRead(BaseModel):
    warehouse_id: int
    warehouse_code: str
    warehouse_name: str
    region: str
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)