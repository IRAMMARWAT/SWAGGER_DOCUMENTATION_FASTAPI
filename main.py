from typing import Annotated, Optional
from fastapi import FastAPI, Path, Query, Body, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime

# ----- Application & Metadata -----
description = """
**Product Inventory API** helps you manage a catalog of items. 🛒

## Features
* List all products with filtering.
* Create new products with full details.
* Update or delete existing products.
"""

tags_metadata = [
    {
        "name": "products",
        "description": "Operations with products. **Create, read, update, and delete** items in the inventory.",
    },
    {
        "name": "health",
        "description": "Simple health checks for the API service.",
    },
]

app = FastAPI(
    title="Product Inventory API",
    description=description,
    version="1.0.0",
    openapi_tags=tags_metadata,
)

# ----- Pydantic Models (Define Data Shapes) -----
class ProductBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, examples=["Wireless Mouse"])
    description: Optional[str] = Field(
        default=None,
        examples=["A high-precision ergonomic mouse with 2.4GHz connectivity."]
    )
    price: float = Field(..., gt=0, examples=[29.99])
    in_stock: bool = Field(default=True)

class ProductCreate(ProductBase):
    """Model for creating a new product."""
    pass

class Product(ProductBase):
    """Full product model, includes system-generated fields."""
    id: int
    created_at: datetime

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 42,
                    "name": "Mechanical Keyboard",
                    "description": "RGB backlit keyboard with blue switches.",
                    "price": 89.99,
                    "in_stock": True,
                    "created_at": "2024-01-18T10:30:00"
                }
            ]
        }
    }

# ----- In-Memory "Database" -----
fake_db = {}
product_counter = 1

# ----- API Endpoints -----
@app.get("/", tags=["health"])
async def root():
    """Root endpoint providing a welcome message."""
    return {"message": "Welcome to the Product Inventory API"}

@app.get("/health", tags=["health"])
async def health_check():
    """Check if the API service is running."""
    return {"status": "healthy", "timestamp": datetime.now()}

@app.get("/products/", response_model=list[Product], tags=["products"])
async def read_products(
    skip: Annotated[int, Query(ge=0, description="Number of items to skip")] = 0,
    limit: Annotated[int, Query(ge=1, le=100, description="Maximum items to return")] = 10,
    in_stock: Optional[bool] = Query(None, description="Filter by availability")
):
    """
    Retrieve a list of products.

    You can paginate results and filter by stock availability.
    """
    filtered_items = list(fake_db.values())
    if in_stock is not None:
        filtered_items = [item for item in filtered_items if item.in_stock == in_stock]
    return filtered_items[skip : skip + limit]

@app.get("/products/{product_id}", response_model=Product, tags=["products"])
async def read_product(
    product_id: Annotated[int, Path(..., title="The ID of the product to get", gt=0)]
):
    """Get a specific product by its unique ID."""
    if product_id not in fake_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return fake_db[product_id]

@app.post("/products/", response_model=Product, tags=["products"], status_code=201)
async def create_product(
    product: Annotated[
        ProductCreate,
        Body(
            examples=[
                {
                    "name": "Webcam 1080p",
                    "description": "Full HD webcam with built-in microphone.",
                    "price": 49.95,
                    "in_stock": True,
                }
            ],
        ),
    ]
):
    """
    Add a new product to the inventory.

    - **name**: Product name (required)
    - **price**: Must be greater than 0
    """
    global product_counter
    # Create a Product instance with system-generated fields
    db_product = Product(
        id=product_counter,
        created_at=datetime.now(),
        **product.model_dump()
    )
    fake_db[product_counter] = db_product
    product_counter += 1
    return db_product

@app.delete("/products/{product_id}", tags=["products"])
async def delete_product(
    product_id: Annotated[int, Path(..., title="The ID of the product to delete", gt=0)]
):
    """Remove a product from the inventory."""
    if product_id not in fake_db:
        raise HTTPException(status_code=404, detail="Product not found")
    del fake_db[product_id]
    return {"message": f"Product {product_id} deleted successfully"}