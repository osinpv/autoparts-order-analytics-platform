from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base
from app.models.mixins import TimestampMixin


class Warehouse(TimestampMixin, Base):
    __tablename__ = "warehouse"
    __table_args__ = {"schema": "autoparts_owner"}

    warehouse_id: Mapped[int] = mapped_column(primary_key=True)
    warehouse_code: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
    warehouse_name: Mapped[str] = mapped_column(String(255), nullable=False)
    region: Mapped[str] = mapped_column(String(100), nullable=False)