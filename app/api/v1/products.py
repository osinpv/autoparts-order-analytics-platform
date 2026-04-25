from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.product import Product
from app.models.product_brand import ProductBrand
from app.models.product_category import ProductCategory
from app.schemas.product import ProductCreate, ProductDetailsRead, ProductRead


router = APIRouter(tags=["products"])


def get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found.")
    return product


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


@router.get("/products/{product_id}", response_model=ProductRead)
def get_product(product_id: int, db: Session = Depends(get_db)):
    return get_product_or_404(product_id, db)


@router.get("/products/{product_id}/details", response_model=ProductDetailsRead)
def get_product_details(product_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(Product, ProductCategory, ProductBrand)
        .join(
            ProductCategory,
            Product.category_id == ProductCategory.category_id,
            isouter=True,
        )
        .join(
            ProductBrand,
            Product.brand_id == ProductBrand.brand_id,
            isouter=True,
        )
        .where(Product.product_id == product_id)
    )

    row = db.execute(stmt).first()

    if row is None:
        raise HTTPException(status_code=404, detail="Product not found.")

    product, category, brand = row

    return ProductDetailsRead(
        product_id=product.product_id,
        sku=product.sku,
        product_name=product.product_name,
        category_id=product.category_id,
        category_name=category.category_name if category else None,
        brand_id=product.brand_id,
        brand_name=brand.brand_name if brand else None,
        price=product.price,
        is_active=product.is_active,
        created_datetime=product.created_datetime,
        updated_datetime=product.updated_datetime,
    )