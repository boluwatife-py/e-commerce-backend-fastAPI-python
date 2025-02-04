# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from app.database import SessionLocal
# from app.crud import create_user, get_user_by_email
# from app.schemas import UserCreate, UserResponse

# router = APIRouter()


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()

# @router.post("/users", response_model=UserResponse)
# def register_user(user: UserCreate, db: Session = Depends(get_db)):
#     db_user = get_user_by_email(db, user.email)
#     if db_user:
#         raise HTTPException(status_code=400, detail="Email already registered")
    
#     return create_user(db, user)
