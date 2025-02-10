from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from app.database import get_db
from app.crud import create_user, get_user_by_email, get_user_by_phone
from app.models import User
from app.schemas import UserCreate, Token, LoginRequest, TokenRefreshRequest
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, create_verification_token
from fastapi import BackgroundTasks
from core.email_utils import send_verification_email

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/signup", response_model=Token)
def register_user(user: UserCreate, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    db_user_email = get_user_by_email(db, user.email)
    db_user_phone = get_user_by_phone(db, user.phone)
    
    if db_user_email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    if db_user_phone:
        raise HTTPException(status_code=400, detail="Phone already registered")

    user.password = hash_password(user.password)
    db_user = create_user(db, user)
    
    verification_token = create_verification_token(db_user.email)
    background_tasks.add_task(send_verification_email, db_user.email, verification_token)
    
    access_token = create_access_token({"sub": db_user.email, "role": db_user.role})
    refresh_token = create_refresh_token({"sub": db_user.email})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token", response_model=Token)
def refresh_token(token_data: TokenRefreshRequest):
    try:
        payload = verify_token(token_data.refresh_token)
        email: str = payload.get("sub")

        if not email:
            raise HTTPException(status_code=401, detail="Invalid refresh token")

        new_access_token = create_access_token({"sub": email})
        return {"access_token": new_access_token, "refresh_token": token_data.refresh_token, "token_type": "bearer"}

    except HTTPException:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
