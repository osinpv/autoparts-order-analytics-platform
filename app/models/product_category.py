from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class ProductCategory(TimestampMixin, Base):
    __tablename__ = "product_category"
    __table_args__ = {"schema": "autoparts_owner"}

    category_id: Mapped[int] = mapped_column(primary_key=True)
    category_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    parent_category_id: Mapped[int | None] = mapped_column(
        ForeignKey("autoparts_owner.product_category.category_id"),
        nullable=True,
    )