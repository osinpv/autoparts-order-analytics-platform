from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InventoryMovement(Base):
    __tablename__ = "inventory_movement"
    __table_args__ = (
        Index(
            "ix_inventory_movement_warehouse_product",
            "warehouse_id",
            "product_id",
        ),
        CheckConstraint(
            "movement_type in ('INITIAL_LOAD', 'RECEIVE', 'RESERVE', 'RELEASE', 'SHIP', 'ADJUSTMENT')",
            name="ck_inventory_movement_type_allowed",
        ),
        CheckConstraint(
            "reference_type is null or reference_type in ('INVENTORY_BALANCE', 'MANUAL', 'ORDER', 'ORDER_ITEM', 'SHIPMENT')",
            name="ck_inventory_movement_reference_type_allowed",
        ),
        CheckConstraint(
            "qty > 0",
            name="ck_inventory_movement_qty_positive",
        ),
        CheckConstraint(
            "resulting_on_hand_qty >= 0",
            name="ck_inventory_movement_resulting_on_hand_nonnegative",
        ),
        CheckConstraint(
            "resulting_reserved_qty >= 0",
            name="ck_inventory_movement_resulting_reserved_nonnegative",
        ),
        CheckConstraint(
            "resulting_reserved_qty <= resulting_on_hand_qty",
            name="ck_inventory_movement_resulting_reserved_not_gt_on_hand",
        ),
        {"schema": "autoparts_owner"},
    )

    inventory_movement_id: Mapped[int] = mapped_column(primary_key=True)

    warehouse_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.warehouse.warehouse_id"),
        nullable=False,
    )
    product_id: Mapped[int] = mapped_column(
        ForeignKey("autoparts_owner.product.product_id"),
        nullable=False,
    )

    movement_type: Mapped[str] = mapped_column(String(50), nullable=False)
    qty: Mapped[int] = mapped_column(Integer, nullable=False)

    resulting_on_hand_qty: Mapped[int] = mapped_column(Integer, nullable=False)
    resulting_reserved_qty: Mapped[int] = mapped_column(Integer, nullable=False)

    reference_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    reference_id: Mapped[int | None] = mapped_column(nullable=True)
    comment_text: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_datetime: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )