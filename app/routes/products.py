from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from app.models import Product
from app.schemas import ProductBase, ProductCreate
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, create_verification_token, verify_verification_token, create_password_reset_token, oauth2_scheme, require_role


router = APIRouter()


@router.post("/products/", status_code=status.HTTP_201_CREATED)
def create_product(product: ProductCreate, db: Session = Depends(get_db), user=Depends(require_role(["seller"]))):
    """Create a new product (Only sellers can do this)."""

    new_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id,
        brand=product.brand,
        images=product.images,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return {"message": "Product created successfully", "product": new_product}
    


@router.get('/{product_id}', response_model=ProductBase)
def view_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return ProductBase.model_validate(product, from_attributes=True)
