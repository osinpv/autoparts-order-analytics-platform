from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.v1.error_handlers import handle_integrity_error
from app.core.db import get_db
from app.models.product_brand import ProductBrand
from app.schemas.product_brand import ProductBrandCreate, ProductBrandRead
from app.services.brands_service import get_brand_or_404

router = APIRouter(tags=["brands"])



@router.post("/brands", response_model=ProductBrandRead)
def create_brand(
    payload: ProductBrandCreate,
    db: Session = Depends(get_db),
):
    brand = ProductBrand(
        brand_name=payload.brand_name,
    )
    db.add(brand)

    try:
        db.commit()
    except IntegrityError as exc:
        handle_integrity_error(db, exc)

    db.refresh(brand)
    return brand


@router.get("/brands", response_model=list[ProductBrandRead])
def get_brands(db: Session = Depends(get_db)):
    stmt = select(ProductBrand).order_by(ProductBrand.brand_id)
    brands = db.execute(stmt).scalars().all()
    return brands


@router.get("/brands/{brand_id}", response_model=ProductBrandRead)
def get_brand(brand_id: int, db: Session = Depends(get_db)):
    return get_brand_or_404(brand_id, db)