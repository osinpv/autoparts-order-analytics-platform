from decimal import Decimal

from sqlalchemy import CheckConstraint, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class SalesOrder(TimestampMixin, Base):
    __tablename__ = "sales_order"
    __table_args__ = (
        CheckConstraint(
            "order_status in ('NEW', 'RESERVED', 'RELEASED', 'SHIPPED', 'CANCELLED', 'RETURNED', 'DELIVERED')",
            name="ck_sales_order_status_allowed",
        ),
        {"schema": "autoparts_owner"},
    )

    order_id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    customer_email: Mapped[str] = mapped_column(String(255), nullable=False)
    order_status: Mapped[str] = mapped_column(String(30), nullable=False)
    order_total_amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)