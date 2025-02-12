from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from core.database import get_db
from app.models import Product, User
from app.schemas import ProductResponse, ProductCreate, ReviewResponse
from core.auth import get_current_user, oauth2_scheme, require_role
from typing import Annotated

router = APIRouter()

@router.get("/upgrade-to-merchant")
def upgrade_to_merchant(
    current_user: Annotated[User, Depends(require_role(['buyer']))],
    db: Session = Depends(get_db)
):

    current_user.role = "merchant"
    db.commit()
    db.refresh(current_user)

    return {"message": "You have been upgraded to a merchant"}