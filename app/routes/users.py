from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import create_user, get_user_by_email
from app.schemas import UserCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/users", response_model=UserCreate)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    
    hashed_password = pwd_context.hash(user.password)
    db_user = create_user(db, user)
    db_user.password_hash = hashed_password
    
    return db_user
