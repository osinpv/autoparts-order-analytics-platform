from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductRead

router = APIRouter(tags=["products"])


@router.post("/products", response_model=ProductRead)
def create_product(
    payload: ProductCreate,
    db: Session = Depends(get_db),
):
    product = Product(
        sku=payload.sku,
        product_name=payload.product_name,
        category_id=payload.category_id,
        brand_id=payload.brand_id,
        price=payload.price,
        is_active=payload.is_active,
    )
    db.add(product)

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(product)
    return product


@router.get("/products", response_model=list[ProductRead])
def get_products(db: Session = Depends(get_db)):
    stmt = select(Product).order_by(Product.product_id)
    products = db.execute(stmt).scalars().all()
    return products