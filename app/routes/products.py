from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from app.models import Product, User
from app.schemas import ProductResponse, ProductCreate, ReviewResponse
from core.auth import get_current_user, oauth2_scheme
from typing import Annotated


router = APIRouter()


@router.post("/", response_model=ProductResponse)
def create_product(
    product: ProductCreate,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Session = Depends(get_db), 
):
    if current_user.role != "seller":
        raise HTTPException(status_code=403, detail="Only sellers can add products")

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        seller_id=current_user.user_id,  # ✅ Ensure seller_id is set
        brand=product.brand,
        images=product.images
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    return new_product


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """Retrieve a single product by ID (with reviews & user ID)."""
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        brand=product.brand,
        images=product.images.split(",") if product.images else [],
        created_by=product.created_by,
        reviews=[
            ReviewResponse(id=rev.id, user_id=rev.user_id, rating=rev.rating, comment=rev.comment)
            for rev in product.reviews
        ],
    )
