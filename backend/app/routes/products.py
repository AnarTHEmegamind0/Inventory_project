"""
Product CRUD API endpoints.
Manages product inventory records in MongoDB.
"""

from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..database import get_products_collection

router = APIRouter()


class ProductCreate(BaseModel):
    """Request body for creating a product."""
    name: str
    category: str
    expected_count: int = 0
    location: str = ""
    sku: str = ""
    description: str = ""


class ProductUpdate(BaseModel):
    """Request body for updating a product."""
    name: Optional[str] = None
    category: Optional[str] = None
    expected_count: Optional[int] = None
    location: Optional[str] = None
    sku: Optional[str] = None
    description: Optional[str] = None


@router.post("/")
async def create_product(product: ProductCreate):
    """Create a new product record."""
    collection = get_products_collection()

    # Check for duplicate name
    existing = await collection.find_one({"name": product.name})
    if existing:
        raise HTTPException(status_code=400, detail="Product with this name already exists")

    product_dict = product.model_dump()
    product_dict["created_at"] = datetime.now().isoformat()
    product_dict["updated_at"] = datetime.now().isoformat()

    result = await collection.insert_one(product_dict)

    product_dict.pop("_id", None)
    return {"message": "Product created", "product": product_dict}


@router.get("/")
async def list_products(
    category: Optional[str] = None,
    location: Optional[str] = None,
    limit: int = 50,
    skip: int = 0
):
    """List all products with optional filtering."""
    collection = get_products_collection()

    query = {}
    if category:
        query["category"] = category
    if location:
        query["location"] = location

    cursor = collection.find(query, {"_id": 0}).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    total = await collection.count_documents(query)

    return {"products": products, "total": total}


@router.get("/{product_name}")
async def get_product(product_name: str):
    """Get a specific product by name."""
    collection = get_products_collection()
    product = await collection.find_one({"name": product_name}, {"_id": 0})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.put("/{product_name}")
async def update_product(product_name: str, update: ProductUpdate):
    """Update a product record."""
    collection = get_products_collection()

    update_data = {k: v for k, v in update.model_dump().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    update_data["updated_at"] = datetime.now().isoformat()

    result = await collection.update_one(
        {"name": product_name},
        {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated"}


@router.delete("/{product_name}")
async def delete_product(product_name: str):
    """Delete a product record."""
    collection = get_products_collection()

    result = await collection.delete_one({"name": product_name})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product deleted"}


@router.get("/inventory/summary")
async def get_inventory_summary():
    """Get inventory summary grouped by category."""
    collection = get_products_collection()

    pipeline = [
        {
            "$group": {
                "_id": "$category",
                "total_products": {"$sum": 1},
                "total_expected": {"$sum": "$expected_count"},
            }
        },
        {"$sort": {"_id": 1}},
    ]

    cursor = collection.aggregate(pipeline)
    categories = await cursor.to_list(length=100)

    return {"categories": categories}
