from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product_brand import ProductBrand

def get_brand_or_404(brand_id: int, db: Session) -> ProductBrand:
    brand = db.get(ProductBrand, brand_id)
    if brand is None:
        raise HTTPException(status_code=404, detail="Brand not found.")
    return brand

