from fastapi import FastAPI, HTTPException, Depends
from motor.motor_asyncio import AsyncIOMotorClient
from prometheus_client import make_asgi_app, Counter, Histogram
from typing import List, Optional
import uvicorn

from models import Product, ProductCreate, ProductUpdate
from database import get_database

app = FastAPI(title="Catalog Service", version="1.0.0")

# Add prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Prometheus metrics
PRODUCT_COUNTER = Counter('product_operations_total', 'Total number of product operations')
REQUEST_LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')

@app.on_event("startup")
async def startup_db_client():
    app.mongodb_client = AsyncIOMotorClient("mongodb://catalog-db:27017")
    app.mongodb = app.mongodb_client.catalog_db

@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongodb_client.close()

@app.post("/products/", response_model=Product)
async def create_product(product: ProductCreate, db=Depends(get_database)):
    """Create a new product."""
    PRODUCT_COUNTER.inc()
    
    product_dict = product.dict()
    result = await db["products"].insert_one(product_dict)
    created_product = await db["products"].find_one({"_id": result.inserted_id})
    return Product(**created_product)

@app.get("/products/", response_model=List[Product])
async def list_products(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db=Depends(get_database)
):
    """List all products with optional filtering."""
    query = {}
    if category:
        query["category"] = category
    
    cursor = db["products"].find(query).skip(skip).limit(limit)
    products = await cursor.to_list(length=limit)
    return [Product(**product) for product in products]

@app.get("/products/{product_id}", response_model=Product)
async def get_product(product_id: str, db=Depends(get_database)):
    """Get a specific product by ID."""
    if (product := await db["products"].find_one({"_id": product_id})) is not None:
        return Product(**product)
    raise HTTPException(status_code=404, detail="Product not found")

@app.put("/products/{product_id}", response_model=Product)
async def update_product(
    product_id: str,
    product_update: ProductUpdate,
    db=Depends(get_database)
):
    """Update a product."""
    PRODUCT_COUNTER.inc()
    
    update_result = await db["products"].update_one(
        {"_id": product_id}, {"$set": product_update.dict(exclude_unset=True)}
    )
    
    if update_result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
        
    if (product := await db["products"].find_one({"_id": product_id})) is not None:
        return Product(**product)

@app.delete("/products/{product_id}")
async def delete_product(product_id: str, db=Depends(get_database)):
    """Delete a product."""
    PRODUCT_COUNTER.inc()
    
    delete_result = await db["products"].delete_one({"_id": product_id})
    if delete_result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8002)
