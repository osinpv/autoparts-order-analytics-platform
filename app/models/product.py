from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Product(TimestampMixin, Base):
    __tablename__ = "product"
    __table_args__ = {"schema": "autoparts_owner"}

    product_id: Mapped[int] = mapped_column(primary_key=True)
    sku: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)

    category_id: Mapped[int | None] = mapped_column(
        ForeignKey("autoparts_owner.product_category.category_id"),
        nullable=True,
    )
    brand_id: Mapped[int | None] = mapped_column(
        ForeignKey("autoparts_owner.product_brand.brand_id"),
        nullable=True,
    )

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)