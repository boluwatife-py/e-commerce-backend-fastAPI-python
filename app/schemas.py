from pydantic import BaseModel, EmailStr, condecimal, validator, Field, HttpUrl, field_validator
from decimal import Decimal
from typing import Optional, List, Annotated
from enum import Enum
import re
from datetime import datetime


# User Schema
class UserBase(BaseModel):
    first_name: str = Field(..., example="John")
    last_name: str = Field(..., example="Doe")
    email: EmailStr = Field(..., example="user@example.com")
    phone: str = Field(..., example="+1234567890")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Invalid phone number format")
        return v

class UserCreate(UserBase):
    password: str = Field(..., example="Secure@123")
    
    @validator('password')
    def validate_password(cls, v):
        password_pattern = r"^(?=.*[A-Z])(?=.*[0-9])(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$"
        if not re.fullmatch(password_pattern, v):
            raise ValueError("Password must contain at least one uppercase letter, one number, one special character, and be at least 8 characters long.")
        return v

class UserResponse(BaseModel):
    email: EmailStr = Field(..., example="example@example.com")

class RequestVerificationLink(BaseModel):
    email: EmailStr = Field(..., example="email@example.com")

class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: Decimal
    stock_quantity: int
    category_id: Optional[int]

class ProductCreate(BaseModel):
    name: str
    description: Optional[str] = None
    price: Annotated[Decimal, Field(
        decimal_places=2,
        max_digits=12,
        nullable=False
    )] = Field(nullable=False)
    
    stock_quantity: int
    category_id: Optional[int] = None
    brand: Optional[str] = None
    images: Optional[List] = None

    @field_validator("images")
    @classmethod
    def validate_images(cls, images):
        if len(images) > 10:
            raise ValueError("A product can have a maximum of 10 images")
        return images
    
    class Config:
        from_attributes = True

class ProductResponse(BaseModel):
    product_id: int
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    category_id: Optional[int] = None
    brand: Optional[str] = None
    images: Optional[List[HttpUrl]] = []
    seller_id: int
    created_at: datetime
    updated_at: datetime
    reviews: List

    class Config:
        from_attributes = True


class ReviewResponse(BaseModel):
    id: int
    user_id: int
    rating: int
    comment: Optional[str] = None


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

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    
class TokenRefreshRequest(BaseModel):
    refresh_token: str = Field(..., example='xxxxxx.xxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxx')

class TokenRefreshResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class PasswordResetRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str = Field(..., example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...")
    new_password: str = Field(..., example="Secure@123")
