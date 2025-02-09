from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.crud import create_user, get_user_by_email, get_user_by_phone
from app.schemas import UserCreate, UserResponse
from passlib.context import CryptContext
import jwt
from app.models import User
from app.schemas import Token, LoginRequest
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

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


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/login", response_model=Token)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not pwd_context.verify(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email, "role": user.role})
    return {"access_token": access_token, "token_type": "bearer"}