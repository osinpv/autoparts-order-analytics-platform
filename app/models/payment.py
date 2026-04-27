from datetime import datetime
from decimal import Decimal

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Payment(TimestampMixin, Base):
    __tablename__ = "payment"
    __table_args__ = (
        CheckConstraint(
            "payment_status in ('PENDING', 'PAID', 'FAILED', 'REFUNDED')",
            name="ck_payment_status_allowed",
        ),
        CheckConstraint(
            "payment_method in ('CARD', 'PAYPAL', 'BANK_TRANSFER')",
            name="ck_payment_method_allowed",
        ),
        CheckConstraint(
            "amount >= 0",
            name="ck_payment_amount_nonnegative",
        ),
        {"schema": "autoparts_owner"},
    )

    payment_id: Mapped[int] = mapped_column(primary_key=True)
    payment_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    order_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.sales_order.order_id"),
        nullable=False,
    )

    payment_status: Mapped[str] = mapped_column(String(30), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(30), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)

    paid_datetime: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )