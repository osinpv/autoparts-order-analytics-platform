from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class ProductBrand(TimestampMixin, Base):
    __tablename__ = "product_brand"
    __table_args__ = {"schema": "autoparts_owner"}

    brand_id: Mapped[int] = mapped_column(primary_key=True)
    brand_name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)