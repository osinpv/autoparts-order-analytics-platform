from decimal import Decimal

from sqlalchemy import CheckConstraint, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class SalesOrderItem(TimestampMixin, Base):
    __tablename__ = "sales_order_item"
    __table_args__ = (
        CheckConstraint(
            "qty > 0",
            name="ck_sales_order_item_qty_positive",
        ),
        CheckConstraint(
            "unit_price >= 0",
            name="ck_sales_order_item_unit_price_nonnegative",
        ),
        CheckConstraint(
            "line_amount >= 0",
            name="ck_sales_order_item_line_amount_nonnegative",
        ),
        {"schema": "autoparts_owner"},
    )

    order_item_id: Mapped[int] = mapped_column(primary_key=True)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.sales_order.order_id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.product.product_id"),
        nullable=False,
    )
    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.warehouse.warehouse_id"),
        nullable=False,
    )

    qty: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    line_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)