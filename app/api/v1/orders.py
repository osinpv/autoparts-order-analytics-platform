from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.models.shipment import Shipment
from app.models.enums import (
    InventoryMovementType,
    InventoryReferenceType,
    OrderStatus,
    ShipmentStatus,
)
from app.schemas.sales_order import (
    SalesOrderCreate,
    SalesOrderDetailsRead,
    SalesOrderRead,
)
from app.services.inventory_service import (
    get_inventory_balance_for_update_by_business_key_or_404,
    reserve_inventory_balance,
    release_inventory_balance,
    ship_inventory_balance,
    receive_inventory_balance,
)
from app.services.products_service import get_product_or_404
from app.services.orders_service import (
    get_order_or_404, 
    get_order_items, 
    to_sales_order_read, 
    to_sales_order_item_read
)
from app.services.shipments_service import generate_shipment_number
from app.services.payments_service import has_paid_payment_for_order


router = APIRouter(tags=["orders"])



@router.post("/orders", response_model=SalesOrderRead)
def create_order(
    payload: SalesOrderCreate,
    db: Session = Depends(get_db),
):
    order_total_amount = Decimal("0.00")

    order = SalesOrder(
        order_number=payload.order_number,
        customer_email=payload.customer_email,
        order_status=OrderStatus.NEW.value,
        order_total_amount=Decimal("0.00"),
    )
    db.add(order)
    db.flush()

    for item_payload in payload.items:
        product = get_product_or_404(item_payload.product_id, db)

        unit_price = product.price
        line_amount = unit_price * item_payload.qty
        order_total_amount += line_amount

        order_item = SalesOrderItem(
            order_id=order.order_id,
            product_id=item_payload.product_id,
            warehouse_id=item_payload.warehouse_id,
            qty=item_payload.qty,
            unit_price=unit_price,
            line_amount=line_amount,
        )
        db.add(order_item)

    order.order_total_amount = order_total_amount

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)


@router.get("/orders", response_model=list[SalesOrderRead])
def get_orders(db: Session = Depends(get_db)):
    stmt = select(SalesOrder).order_by(SalesOrder.order_id)
    orders = db.execute(stmt).scalars().all()
    return [to_sales_order_read(order) for order in orders]


@router.get("/orders/{order_id}", response_model=SalesOrderRead)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)
    return to_sales_order_read(order)


@router.get("/orders/{order_id}/details", response_model=SalesOrderDetailsRead)
def get_order_details(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    stmt = (
        select(SalesOrderItem)
        .where(SalesOrderItem.order_id == order_id)
        .order_by(SalesOrderItem.order_item_id)
    )
    items = db.execute(stmt).scalars().all()

    return SalesOrderDetailsRead(
        order_id=order.order_id,
        order_number=order.order_number,
        customer_email=order.customer_email,
        order_status=order.order_status,
        order_total_amount=order.order_total_amount,
        created_datetime=order.created_datetime,
        updated_datetime=order.updated_datetime,
        items=[to_sales_order_item_read(item) for item in items],
    )


@router.post("/orders/{order_id}/reserve", response_model=SalesOrderRead)
def reserve_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    if order.order_status != OrderStatus.NEW.value:
        raise HTTPException(
            status_code=400,
            detail="Only orders in NEW status can be reserved.",
        )

    items = get_order_items(order_id, db)

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Cannot reserve an order without items.",
        )

    for item in items:
        balance = get_inventory_balance_for_update_by_business_key_or_404(
            warehouse_id=item.warehouse_id,
            product_id=item.product_id,
            db=db,
        )

        reserve_inventory_balance(
            balance=balance,
            qty=item.qty,
            db=db,
            movement_type=InventoryMovementType.RESERVE.value,
            reference_type=InventoryReferenceType.ORDER_ITEM.value,
            reference_id=item.order_item_id,
            comment_text=f"Inventory reserved for order {order.order_number}.",
        )

    order.order_status = OrderStatus.RESERVED.value

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)


@router.post("/orders/{order_id}/release", response_model=SalesOrderRead)
def release_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    if order.order_status != OrderStatus.RESERVED.value:
        raise HTTPException(
            status_code=400,
            detail="Only orders in RESERVED status can be released.",
        )

    items = get_order_items(order_id, db)

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Cannot release an order without items.",
        )

    for item in items:
        balance = get_inventory_balance_for_update_by_business_key_or_404(
            warehouse_id=item.warehouse_id,
            product_id=item.product_id,
            db=db,
        )

        release_inventory_balance(
            balance=balance,
            qty=item.qty,
            db=db,
            movement_type=InventoryMovementType.RELEASE.value,
            reference_type=InventoryReferenceType.ORDER_ITEM.value,
            reference_id=item.order_item_id,
            comment_text=f"Inventory released for order {order.order_number}.",
        )

    order.order_status = OrderStatus.RELEASED.value

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)


@router.post("/orders/{order_id}/ship", response_model=SalesOrderRead)
def ship_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    if order.order_status != OrderStatus.RESERVED.value:
        raise HTTPException(
            status_code=400,
            detail="Only orders in RESERVED status can be shipped.",
        )

    if not has_paid_payment_for_order(order.order_id, db):
        raise HTTPException(
            status_code=400,
            detail="Order must have a PAID payment before shipment.",
        )

    items = get_order_items(order_id, db)

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Cannot ship an order without items.",
        )

    for item in items:
        balance = get_inventory_balance_for_update_by_business_key_or_404(
            warehouse_id=item.warehouse_id,
            product_id=item.product_id,
            db=db,
        )

        ship_inventory_balance(
            balance=balance,
            qty=item.qty,
            db=db,
            movement_type=InventoryMovementType.SHIP.value,
            reference_type=InventoryReferenceType.ORDER_ITEM.value,
            reference_id=item.order_item_id,
            comment_text=f"Inventory shipped for order {order.order_number}.",
        )

    shipment = Shipment(
        shipment_number=generate_shipment_number(order.order_id),
        order_id=order.order_id,
        shipment_status=ShipmentStatus.SHIPPED.value,
        carrier_name=None,
        tracking_number=None,
        shipped_datetime=datetime.now(timezone.utc),
    )
    db.add(shipment)

    order.order_status = OrderStatus.SHIPPED.value

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)


@router.post("/orders/{order_id}/cancel", response_model=SalesOrderRead)
def cancel_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    if order.order_status == OrderStatus.SHIPPED.value:
        raise HTTPException(
            status_code=400,
            detail="Shipped orders cannot be cancelled.",
        )

    if order.order_status == OrderStatus.CANCELLED.value:
        raise HTTPException(
            status_code=400,
            detail="Order is already cancelled.",
        )

    if order.order_status == OrderStatus.NEW.value:
        order.order_status = OrderStatus.CANCELLED.value

    elif order.order_status == OrderStatus.RELEASED.value:
        order.order_status = OrderStatus.CANCELLED.value

    elif order.order_status == OrderStatus.RESERVED.value:
        items = get_order_items(order_id, db)

        if not items:
            raise HTTPException(
                status_code=400,
                detail="Cannot cancel a reserved order without items.",
            )

        for item in items:
            balance = get_inventory_balance_for_update_by_business_key_or_404(
                warehouse_id=item.warehouse_id,
                product_id=item.product_id,
                db=db,
            )

            release_inventory_balance(
                balance=balance,
                qty=item.qty,
                db=db,
                movement_type=InventoryMovementType.RELEASE.value,
                reference_type=InventoryReferenceType.ORDER_ITEM.value,
                reference_id=item.order_item_id,
                comment_text=f"Inventory released due to cancellation of order {order.order_number}.",
            )

        order.order_status = OrderStatus.CANCELLED.value

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Order status {order.order_status} is not supported for cancellation.",
        )

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)


@router.post("/orders/{order_id}/return", response_model=SalesOrderRead)
def return_order(order_id: int, db: Session = Depends(get_db)):
    order = get_order_or_404(order_id, db)

    if order.order_status == OrderStatus.RETURNED.value:
        raise HTTPException(
            status_code=400,
            detail="Order is already returned.",
        )

    if order.order_status not in {
        OrderStatus.SHIPPED.value,
        OrderStatus.DELIVERED.value,
    }:
        raise HTTPException(
            status_code=400,
            detail="Only shipped or delivered orders can be returned.",
        )

    items = get_order_items(order_id, db)

    if not items:
        raise HTTPException(
            status_code=400,
            detail="Cannot return an order without items.",
        )

    for item in items:
        balance = get_inventory_balance_for_update_by_business_key_or_404(
            warehouse_id=item.warehouse_id,
            product_id=item.product_id,
            db=db,
        )

        receive_inventory_balance(
            balance=balance,
            qty=item.qty,
            db=db,
            movement_type=InventoryMovementType.RETURN.value,
            reference_type=InventoryReferenceType.ORDER_ITEM.value,
            reference_id=item.order_item_id,
            comment_text=f"Inventory returned from shipped order {order.order_number}.",
        )

    order.order_status = OrderStatus.RETURNED.value

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(order)
    return to_sales_order_read(order)