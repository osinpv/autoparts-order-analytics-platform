from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Shipment(TimestampMixin, Base):
    __tablename__ = "shipment"
    __table_args__ = (
        CheckConstraint(
            "shipment_status in ('CREATED', 'SHIPPED', 'DELIVERED', 'RETURNED')",
            name="ck_shipment_status_allowed",
        ),
        {"schema": "autoparts_owner"},
    )

    shipment_id: Mapped[int] = mapped_column(primary_key=True)
    shipment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.sales_order.order_id"),
        nullable=False,
    )

    shipment_status: Mapped[str] = mapped_column(String(30), nullable=False)
    carrier_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tracking_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    shipped_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )