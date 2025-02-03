from sqlalchemy import Column, Integer, String, Enum, Text, TIMESTAMP, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.sql import func
from .database import Base

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
    
    role = Column(Enum("admin", "buyer", "seller", name="user_roles"), default="buyer", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships (for seller items if needed)
    items = relationship("Item", back_populates="seller")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
