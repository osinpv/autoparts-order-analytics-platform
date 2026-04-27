from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.product import Product


def get_product_or_404(product_id: int, db: Session) -> Product:
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail=f"Product not found: product_id={product_id}.")
    return product



