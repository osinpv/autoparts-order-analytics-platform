from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.sales_order import SalesOrder
from app.models.sales_order_item import SalesOrderItem
from app.schemas.sales_order import (
    SalesOrderItemRead,
    SalesOrderRead,
)


def get_order_or_404(order_id: int, db: Session) -> SalesOrder:
    order = db.get(SalesOrder, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order not found: order_id={order_id}.")
    return order


def get_order_items(order_id: int, db: Session) -> list[SalesOrderItem]:
    stmt = (
        select(SalesOrderItem)
        .where(SalesOrderItem.order_id == order_id)
        .order_by(SalesOrderItem.order_item_id)
    )
    return db.execute(stmt).scalars().all()


def to_sales_order_read(order: SalesOrder) -> SalesOrderRead:
    return SalesOrderRead.model_validate(order)


def to_sales_order_item_read(item: SalesOrderItem) -> SalesOrderItemRead:
    return SalesOrderItemRead.model_validate(item)

