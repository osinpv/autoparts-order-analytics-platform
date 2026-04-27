from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.shipment import Shipment
from app.schemas.shipment import ShipmentRead


def get_shipment_or_404(shipment_id: int, db: Session) -> Shipment:
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment


def to_shipment_read(shipment: Shipment) -> ShipmentRead:
    return ShipmentRead.model_validate(shipment)


def generate_shipment_number(order_id: int) -> str:
    return f"SHP-{order_id:06d}"

