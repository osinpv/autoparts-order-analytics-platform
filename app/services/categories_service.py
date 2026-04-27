from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product_category import ProductCategory


def get_category_or_404(category_id: int, db: Session) -> ProductCategory:
    category = db.get(ProductCategory, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found.")
    return category
