from sqlalchemy import Column, Integer, String, Enum, Text, TIMESTAMP, ForeignKey, DECIMAL, Date, CheckConstraint, Boolean, JSON
from sqlalchemy.orm import relationship, validates, session
from sqlalchemy.sql import func
from core.database import Base
from sqlalchemy import Column, String, Boolean, DateTime
from datetime import datetime


class User(Base):
    __tablename__ = "users"

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    address = Column(Text)
    city = Column(String(50))
    state = Column(String(50))
    zip_code = Column(String(10))
    country = Column(String(50))
    is_active = Column(Boolean, default=False, nullable=False)

    role = Column(Enum("admin", "buyer", "merchant", name="user_roles"), default="buyer", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    products = relationship("Product", back_populates="seller", cascade="all, delete", lazy="dynamic")
    orders = relationship("Order", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="user", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="user", cascade="all, delete-orphan")

    # Corrected relationships
    reports_received = relationship(
        "ProductReport",
        foreign_keys='[ProductReport.seller_id]',  # No quotes
        back_populates="reported_seller"
    )

    reports_made = relationship(
        "ProductReport",
        foreign_keys='[ProductReport.user_id]',  # Fixed incorrect reference
        back_populates="reported_by"
    )

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
    images = Column(JSON, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    category = relationship("Category", back_populates="products")
    seller = relationship("User", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")
    reviews = relationship("Review", back_populates="product", cascade="all, delete-orphan")
    wishlists = relationship("Wishlist", back_populates="product", cascade="all, delete-orphan")
    cart = relationship("Cart", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product {self.name} (${self.price}) - Seller ID: {self.seller_id}>"
    

class Category(Base):
    __tablename__ = "categories"

    category_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text)
    parent_category_id = Column(Integer, ForeignKey("categories.category_id", ondelete="SET NULL"), nullable=True)

    # Self-referencing relationship
    parent_category = relationship("Category", remote_side=[category_id], backref="subcategories")

    # Relationship with Products
    products = relationship("Product", back_populates="category")

    def __repr__(self):
        return f"<Category {self.name}>"
    

class Order(Base):
    __tablename__ = "orders"

    order_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    total_amount = Column(DECIMAL(10, 2), nullable=False)
    
    order_status = Column(Enum("pending", "shipped", "delivered", "cancelled", "returned", name="order_status"), default="pending", nullable=False)
    payment_status = Column(Enum("pending", "completed", "failed", name="payment_status"), default="pending", nullable=False)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    coupon_id = Column(Integer, ForeignKey("coupons.coupon_id"), nullable=True)
    

    # Relationships
    user = relationship("User", back_populates="orders")
    order_items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")
    payment = relationship("Payment", back_populates="order", uselist=False, cascade="all, delete-orphan")
    shipping = relationship("Shipping", back_populates="order", uselist=False, cascade="all, delete-orphan")
    coupon = relationship("Coupon", back_populates="orders")

    def __repr__(self):
        return f"<Order {self.order_id} - {self.order_status} (${self.total_amount})>"


class OrderItem(Base):
    __tablename__ = "order_items"

    order_item_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(DECIMAL(10, 2), nullable=False)
    total_price = Column(DECIMAL(10, 2), nullable=False)

    # Relationships
    order = relationship("Order", back_populates="order_items")
    product = relationship("Product", back_populates="order_items")

    def __repr__(self):
        return f"<OrderItem {self.quantity} x Product {self.product_id} (Order {self.order_id})>"
    

class Payment(Base):
    __tablename__ = "payments"

    payment_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)

    payment_method = Column(Enum("credit_card", "paypal", "bank_transfer", "crypto", name="payment_methods"), nullable=False)
    payment_status = Column(Enum("pending", "completed", "failed", name="payment_status"), default="pending", nullable=False)

    transaction_id = Column(String(255), unique=True, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="payment")
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment {self.payment_id} - {self.payment_status} (${self.amount})>"
    

class Shipping(Base):
    __tablename__ = "shipping"

    shipping_id = Column(Integer, primary_key=True, autoincrement=True)
    order_id = Column(Integer, ForeignKey("orders.order_id", ondelete="CASCADE"), nullable=False)
    tracking_number = Column(String(100), unique=True, nullable=True)
    carrier = Column(String(100), nullable=True)
    estimated_delivery_date = Column(Date, nullable=True)

    shipping_status = Column(Enum("pending", "shipped", "delivered", "returned", name="shipping_status"), default="pending", nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationship
    order = relationship("Order", back_populates="shipping")

    def __repr__(self):
        return f"<Shipping {self.shipping_id} - {self.shipping_status} (Tracking: {self.tracking_number})>"


class Review(Base):
    __tablename__ = "reviews"

    review_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Constraints
    __table_args__ = (CheckConstraint("rating BETWEEN 1 AND 5", name="rating_check"),)

    # Relationships
    user = relationship("User", back_populates="reviews")
    product = relationship("Product", back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.review_id} - {self.rating} stars>"


class Wishlist(Base):
    __tablename__ = "wishlists"

    wishlist_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="wishlists")
    product = relationship("Product", back_populates="wishlists")

    def __repr__(self):
        return f"<Wishlist {self.wishlist_id}>"


class Coupon(Base):
    __tablename__ = "coupons"

    coupon_id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False)
    discount_percentage = Column(DECIMAL(5, 2), nullable=False)
    valid_from = Column(Date, nullable=True)
    valid_to = Column(Date, nullable=True)
    min_order_value = Column(DECIMAL(10, 2), default=0)
    max_discount_value = Column(DECIMAL(10, 2), nullable=True)
    status = Column(Enum("active", "expired", "disabled", name="status"), default="active", nullable=False)
    
    
    orders = relationship("Order", back_populates="coupon")

    # Constraints
    __table_args__ = (
        CheckConstraint("discount_percentage BETWEEN 0 AND 100", name="discount_percentage_check"),
    )

    def __repr__(self):
        return f"<Coupon {self.code} - {self.discount_percentage}%>"


class Cart(Base):
    __tablename__ = "cart"

    cart_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.user_id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.product_id", ondelete="CASCADE"), nullable=False)
    quantity = Column(Integer, nullable=False)
    added_at = Column(TIMESTAMP, server_default=func.now())

    # Constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name="quantity_check"),
    )

    # Relationships
    user = relationship("User", back_populates="cart")
    product = relationship("Product", back_populates="cart")

    def __repr__(self):
        return f"<Cart {self.cart_id} - User {self.user_id} - Product {self.product_id}>"


class PasswordResetToken(Base):
    __tablename__ = "password_reset_tokens"

    token = Column(String, primary_key=True, index=True)  # Unique reset token
    email = Column(String, index=True)  # Associated email
    is_used = Column(Boolean, default=False)  # Check if token is used
    created_at = Column(DateTime, default=datetime.utcnow)  # Timestamp


class ProductReport(Base):
    __tablename__ = "product_reports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.product_id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # User who reported
    seller_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)  # Seller of the reported product
    reason = Column(Text, nullable=False)
    reported_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    product = relationship("Product", back_populates="reports")
    reported_by = relationship("User", foreign_keys=[user_id], back_populates="reports_made")  # User who submitted the report
    reported_seller = relationship("User", foreign_keys=[seller_id], back_populates="reports_received")  # Seller who got reported
