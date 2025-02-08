from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import create_user, get_user_by_email, get_user_by_phone
from app.schemas import UserCreate, UserResponse
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user_email = get_user_by_email(db, user.email)
    db_user_phone = get_user_by_phone(db, user.phone)
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db_user_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user.password = pwd_context.hash(user.password)
    db_user = create_user(db, user)
    
    return UserResponse.model_validate(db_user)

