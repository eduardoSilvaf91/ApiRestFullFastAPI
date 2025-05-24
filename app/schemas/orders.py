from datetime import datetime
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from schemas.products import Product

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class PaymentMethod(str, Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BOLETO = "boleto"
    PIX = "pix"
    CASH = "cash"

class OrderItemBase(BaseModel):
    product_id: int
    quantity: int
    unit_price: float
    discount: float = 0.0

class OrderItemCreate(OrderItemBase):
    pass

class OrderItem(OrderItemBase):
    id: int
    total: float
    product: Product

    class Config:
        from_attributes = True

class OrderBase(BaseModel):
    client_id: int
    payment_method: PaymentMethod
    shipping_address: str
    notes: Optional[str] = None
    expected_delivery_date: Optional[datetime] = None

class OrderCreate(OrderBase):
    items: List[OrderItemCreate]

class OrderUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    payment_method: Optional[PaymentMethod] = None
    shipping_address: Optional[str] = None

class Order(OrderBase):
    id: int
    user_id: int
    status: OrderStatus
    total: float
    discount: float = 0.0
    shipping_cost: float = 0.0
    created_at: datetime
    updated_at: datetime
    items: List[OrderItem] = []

    class Config:
        from_attributes = True