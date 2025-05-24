from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class ProductStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    OUT_OF_STOCK = "out_of_stock"

class ImageBase(BaseModel):
    url: str
    order: int

class ProductBase(BaseModel):
    name: str
    description: str
    sale_price: float
    barcode: Optional[str] = None
    category_id: int
    stock: int = 0
    min_stock: int = 5
    expiry_date: Optional[datetime] = None
    status: ProductStatus = ProductStatus.ACTIVE

class ProductCreate(ProductBase):
    images: Optional[List[ImageBase]] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    sale_price: Optional[float] = None
    stock: Optional[int] = None
    status: Optional[ProductStatus] = None

class Product(ProductBase):
    id: int
    created_at: datetime
    updated_at: datetime
    images: List[ImageBase] = []

    class Config:
        from_attributes = True
