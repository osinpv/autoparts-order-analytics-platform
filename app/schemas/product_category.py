from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProductCategoryCreate(BaseModel):
    category_name: str
    parent_category_id: int | None = None


class ProductCategoryRead(BaseModel):
    category_id: int
    category_name: str
    parent_category_id: int | None
    created_datetime: datetime
    updated_datetime: datetime

    model_config = ConfigDict(from_attributes=True)