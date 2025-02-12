from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from core.database import get_db
from app.models import User
from core.auth import require_role
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