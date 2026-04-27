from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.shipment import Shipment
from app.models.sales_order import SalesOrder
from app.models.enums import OrderStatus, ShipmentStatus
from app.schemas.shipment import ShipmentRead, ShipmentUpdate

router = APIRouter(tags=["shipments"])


def get_shipment_or_404(shipment_id: int, db: Session) -> Shipment:
    shipment = db.get(Shipment, shipment_id)
    if shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found.")
    return shipment


def to_shipment_read(shipment: Shipment) -> ShipmentRead:
    return ShipmentRead.model_validate(shipment)


@router.get("/shipments", response_model=list[ShipmentRead])
def get_shipments(
    order_id: int | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(Shipment)

    if order_id is not None:
        stmt = stmt.where(Shipment.order_id == order_id)

    stmt = stmt.order_by(Shipment.shipment_id)

    shipments = db.execute(stmt).scalars().all()
    return [to_shipment_read(shipment) for shipment in shipments]


@router.get("/shipments/{shipment_id}", response_model=ShipmentRead)
def get_shipment(shipment_id: int, db: Session = Depends(get_db)):
    shipment = get_shipment_or_404(shipment_id, db)
    return to_shipment_read(shipment)


@router.patch("/shipments/{shipment_id}", response_model=ShipmentRead)
def update_shipment(
    shipment_id: int,
    payload: ShipmentUpdate,
    db: Session = Depends(get_db),
):
    shipment = get_shipment_or_404(shipment_id, db)

    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(shipment, field, value)

    db.commit()
    db.refresh(shipment)

    return to_shipment_read(shipment)


@router.post("/shipments/{shipment_id}/deliver", response_model=ShipmentRead)
def deliver_shipment(
    shipment_id: int,
    db: Session = Depends(get_db),
):
    shipment = get_shipment_or_404(shipment_id, db)

    if shipment.shipment_status == ShipmentStatus.DELIVERED.value:
        raise HTTPException(
            status_code=400,
            detail="Shipment is already delivered.",
        )

    if shipment.shipment_status != ShipmentStatus.SHIPPED.value:
        raise HTTPException(
            status_code=400,
            detail="Only shipped shipments can be delivered.",
        )

    order = db.get(SalesOrder, shipment.order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Related order not found.")

    shipment.shipment_status = ShipmentStatus.DELIVERED.value
    order.order_status = OrderStatus.DELIVERED.value

    db.commit()
    db.refresh(shipment)

    return to_shipment_read(shipment)