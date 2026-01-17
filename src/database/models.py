"""Database models for products and orders."""

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class OrderStatus(str, Enum):
    """Order status enum."""

    PENDING = "pending"
    CONFIRMED = "confirmed"
    PAID = "paid"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Product(BaseModel):
    """Product model."""

    id: str = Field(alias="_id")
    name: str
    description: str
    price: float
    category: str
    stock: int
    image_url: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True


class OrderItem(BaseModel):
    """Order item model."""

    product_id: str
    product_name: str
    quantity: int
    price: float
    subtotal: float


class Order(BaseModel):
    """Order model."""

    id: str = Field(alias="_id")
    session_id: str
    items: List[OrderItem]
    total: float
    status: OrderStatus = OrderStatus.PENDING
    payment_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    class Config:
        populate_by_name = True
