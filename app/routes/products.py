from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from core.database import get_db
from app.crud import get_user_by_email, get_user_by_phone
from app.models import User, PasswordResetToken
from app.schemas import ProductBase
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, create_verification_token, verify_verification_token, create_password_reset_token
from core.email_utils import send_verification_email, send_reset_password_email


router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.get('/{product_id}', response_model=ProductBase)
def view_product(product_id: int, db: Session = Depends(get_db)):
    # product = db.query(Product).filter(Product.id == product_id).first()
    
    # if not product:
    #     raise HTTPException(status_code=404, detail="Product not found")

    return ProductBase(
        name = "Laptop",
        description = "A powerful laptop",
        price = 1200.99,
        stock_quantity =  10,
        category_id = 1
    )
