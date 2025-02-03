from pydantic import BaseModel, EmailStr, condecimal
from decimal import Decimal
from typing import Optional
from enum import Enum

# Enum for order status
class OrderStatus(str, Enum):
    pending = "pending"
    shipped = "shipped"
    delivered = "delivered"
    cancelled = "cancelled"

# Enum for payment status
class PaymentStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"

# User Schema
class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    role: str

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    category_id: Optional[int]

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    product_id: int

    class Config:
        from_attributes = True


class OrderBase(BaseModel):
    user_id: int
    total_amount: Decimal
    order_status: OrderStatus = OrderStatus.pending
    payment_status: PaymentStatus = PaymentStatus.pending

class OrderCreate(OrderBase):
    pass

class OrderResponse(OrderBase):
    order_id: int

    class Config:
        from_attributes = True

# Order Item Schema
class OrderItemBase(BaseModel):
    order_id: int
    product_id: int
    quantity: int
    unit_price: Decimal

class OrderItemResponse(OrderItemBase):
    order_item_id: int

    class Config:
        from_attributes = True

# Payment Schema
class PaymentBase(BaseModel):
    order_id: int
    user_id: int
    amount: Decimal
    payment_status: PaymentStatus = PaymentStatus.pending

class PaymentCreate(PaymentBase):
    payment_method: str

class PaymentResponse(PaymentBase):
    payment_id: int

    class Config:
        from_attributes = True
