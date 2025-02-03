from sqlalchemy import Column, Integer, String, Enum, Text, TIMESTAMP, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship, validates, session
from datetime import datetime
from sqlalchemy.sql import func
from .database import Base
from decimal import Decimal

class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True)
    address = Column(Text)
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    country = Column(String(50))
    
    role = Column(Enum("admin", "buyer", "merchant", name="user_roles"), default="buyer", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    products = relationship("Product", back_populates="seller", cascade="all, delete", lazy="dynamic")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    

    
class Product(Base):
    __tablename__ = "products"

    product_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    price = Column(DECIMAL(10, 2), nullable=False)
    stock_quantity = Column(Integer, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)
    seller_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    brand = Column(String(100))
    image_url = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    seller = relationship("User", back_populates="products")

    @validates("seller_id")
    def validate_seller(self, key, seller_id):
        seller = session.query(User).filter_by(user_id=seller_id).first()
        if not seller or seller.role != "seller":
            raise ValueError("Only sellers can add products")
        return seller_id

    def __repr__(self):
        return f"<Product {self.name} (${self.price}) - Seller ID: {self.seller_id}>"
    

