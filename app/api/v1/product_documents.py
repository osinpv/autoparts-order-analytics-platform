from datetime import datetime, UTC
from typing import Any

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Query, Depends
from pymongo.errors import DuplicateKeyError

from app.mongo import get_product_documents_collection
from app.schemas.product_document import ProductDocumentCreate, ProductDocumentResponse

from app.core.db import get_db
from sqlalchemy.orm import Session
from app.services.products_service import get_product_or_404

router = APIRouter(
    prefix="/product-documents",
    tags=["Product Documents"],
)


def serialize_product_document(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "product_id": doc["product_id"],
        "sku": doc["sku"],
        "category": doc["category"],
        "attributes": doc.get("attributes", {}),
        "fitment": doc.get("fitment", []),
        "oem_numbers": doc.get("oem_numbers", []),
        "created_at": doc["created_at"],
    }


@router.post("/", response_model=ProductDocumentResponse, status_code=201)
async def create_product_document(
    payload: ProductDocumentCreate,
    db: Session = Depends(get_db),
):
    existing_product =get_product_or_404(payload.product_id, db)

    if existing_product.sku != payload.sku:
        raise HTTPException(
            status_code=400,
            detail=f"SKU mismatch: Existing product sku is {existing_product.sku}, but payload sku is {payload.sku}",
        )
    
    collection = get_product_documents_collection()

    doc = payload.model_dump()
    doc["created_at"] = datetime.now(UTC)

    try:
        result = await collection.insert_one(doc)
    except DuplicateKeyError:
        raise HTTPException(
            status_code=409,
            detail=f"Product document for product_id={payload.product_id} already exists",
        )

    created_doc = await collection.find_one({"_id": result.inserted_id})

    if not created_doc:
        raise HTTPException(status_code=500, detail="Created document was not found")

    return serialize_product_document(created_doc)


@router.get("/{product_id}", response_model=ProductDocumentResponse)
async def get_product_document(product_id: int):
    collection = get_product_documents_collection()

    doc = await collection.find_one({"product_id": product_id})

    if not doc:
        raise HTTPException(
            status_code=404,
            detail=f"Product document for product_id={product_id} was not found",
        )

    return serialize_product_document(doc)


@router.get("/search/by-fitment")
async def search_product_documents_by_fitment(
    make: str = Query(...),
    model: str = Query(...),
    year: int = Query(...),
    engine: str | None = Query(None),
):
    collection = get_product_documents_collection()

    elem_match: dict[str, Any] = {
        "make": make,
        "model": model,
        "year_from": {"$lte": year},
        "year_to": {"$gte": year},
    }

    if engine:
        elem_match["engine"] = engine

    cursor = collection.find({
        "fitment": {
            "$elemMatch": elem_match
        }
    })

    docs = await cursor.to_list(length=100)

    return [serialize_product_document(doc) for doc in docs]