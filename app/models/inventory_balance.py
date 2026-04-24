from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class InventoryBalance(TimestampMixin, Base):
    __tablename__ = "inventory_balance"
    __table_args__ = (
        UniqueConstraint(
            "warehouse_id",
            "product_id",
            name="uq_inventory_balance_warehouse_product",
        ),
        {"schema": "autoparts_owner"},
    )

    inventory_balance_id: Mapped[int] = mapped_column(primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.warehouse.warehouse_id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.product.product_id"),
        nullable=False,
    )

    on_hand_qty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )
    reserved_qty: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )