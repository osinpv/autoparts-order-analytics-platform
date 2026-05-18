from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class FitmentItem(BaseModel):
    make: str
    model: str
    year_from: int
    year_to: int
    engine: str | None = None


class ProductDocumentCreate(BaseModel):
    product_id: int
    sku: str
    category: str
    attributes: dict[str, Any]
    fitment: list[FitmentItem] = Field(default_factory=list)
    oem_numbers: list[str] = Field(default_factory=list)


class ProductDocumentResponse(ProductDocumentCreate):
    id: str
    created_at: datetime