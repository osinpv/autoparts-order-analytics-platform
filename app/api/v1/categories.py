from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.product_category import ProductCategory
from app.schemas.product_category import ProductCategoryCreate, ProductCategoryRead

router = APIRouter(tags=["categories"])


@router.post("/categories", response_model=ProductCategoryRead)
def create_category(
    payload: ProductCategoryCreate,
    db: Session = Depends(get_db),
):
    category = ProductCategory(
        category_name=payload.category_name,
        parent_category_id=payload.parent_category_id,
    )
    db.add(category)

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(category)
    return category


@router.get("/categories", response_model=list[ProductCategoryRead])
def get_categories(db: Session = Depends(get_db)):
    stmt = select(ProductCategory).order_by(ProductCategory.category_id)
    categories = db.execute(stmt).scalars().all()
    return categories