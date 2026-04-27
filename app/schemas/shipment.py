from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ShipmentRead(BaseModel):
    shipment_id: int
    shipment_number: str
    order_id: int
    shipment_status: str
    carrier_name: str | None
    tracking_number: str | None
    shipped_datetime: datetime | None
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)


class ShipmentUpdate(BaseModel):
    carrier_name: str | None = None
    tracking_number: str | None = None