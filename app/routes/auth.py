from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from core.database import get_db
from app.crud import get_user_by_email, get_user_by_phone
from app.models import User
from app.schemas import UserCreate, Token, LoginRequest, TokenRefreshRequest, UserResponse, RequestVerificationLink, PasswordResetRequest, ResetPasswordRequest
from core.auth import hash_password, verify_password, create_access_token, create_refresh_token, verify_token, create_verification_token, verify_verification_token, create_password_reset_token, verify_reset_token
from core.email_utils import send_verification_email, send_reset_password_email
from core.redis import redis_client

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

responces = {
    422: {
        "description": "Validation Error",
        "content": {
            "application/json": {
                "example": {
                    "detail": "Validation Error",
                    "errors": [
                        {"field": "body.phone", "message": "Invalid phone number format"},
                        {"field": "body.password", "message": "Password must meet security requirements"}
                    ]
                }
            }
        }
    }
}

@router.post("/signup/", response_model=UserResponse, responses=responces)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        if get_user_by_email(db, user.email):
            raise HTTPException(status_code=400, detail="Email already registered")
        
        if get_user_by_phone(db, user.phone):
            raise HTTPException(status_code=400, detail="Phone already registered")

        user.password = hash_password(user.password)
        db_user = User(email=user.email, first_name=user.first_name, last_name=user.last_name, password_hash=user.password, phone=user.phone)
        db.add(db_user)

        verification_token = create_verification_token(user.email)
        send_verification_email(user.email, verification_token)

        db.commit()
        db.refresh(db_user)

        return UserResponse(
            email=db_user.email
        )

    except HTTPException:
        db.rollback()
        raise

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.") 


@router.post("/request-verification-link/")
def request_new_verification_link(data: RequestVerificationLink, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == data.email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_active:
            raise HTTPException(status_code=400, detail="Email is already verified")

        verification_token = create_verification_token(user.email)
        send_verification_email(user.email, verification_token)

        return {"message": "A new verification link has been sent to your email"}

    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        raise HTTPException(status_code=500, detail="Something went wrong. Please try again.")


@router.get('/verify-email/')
def verify_account(token: str, db: Session = Depends(get_db)):
    try:
        email = verify_verification_token(token)
        if not email:
            raise HTTPException(status_code=400, detail="Invalid or expired token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if user.is_active:
            return {"message": "Email is already verified"}

        user.is_active = True
        db.commit()

        return {"message": "Email successfully verified. You can now log in.", 'redirect_url': '/'}

    except HTTPException as http_exc:
        raise http_exc

    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="An error occurred while verifying the account.")


@router.post("/login", response_model=Token)
def login(user_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()

    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.email, "role": user.role})
    refresh_token = create_refresh_token({"sub": user.email})

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/refresh-token/", response_model=Token)
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


def store_reset_token(email: str, token: str):
    """Store password reset token in Redis with an expiry."""
    redis_client.setex(f"reset_token:{email}", 1800, token)
    
@router.post("/forgot-password/")
def forgot_password(
    data: PasswordResetRequest, 
    db: Session = Depends(get_db), 
    authorization: str = Header(None)  # Token in the header
):
    """
    Allows only unauthenticated users to request a password reset.
    If a valid token is provided in the Authorization header, reject the request.
    """

    if authorization:
        try:
            verify_token(authorization.replace("Bearer ", ""))
            raise HTTPException(status_code=400, detail="You are already logged in")
        except:
            pass  # If token is invalid, ignore and proceed

    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    reset_token = create_password_reset_token(user.email)
    store_reset_token(user.email, reset_token)
    send_reset_password_email(user.email, reset_token)

    return {"message": "A password reset link has been sent to your email"}


@router.post("/reset-password/")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    email = verify_reset_token(data.token)  # Get email from Redis
    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired token")

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if verify_password(data.new_password, user.password_hash):
        raise HTTPException(status_code=400, detail="New password cannot be the same as the old password")

    user.password_hash = hash_password(data.new_password)
    db.commit()

    redis_client.delete(f"reset_token:{email}")  # Remove the token from Redis

    return {"message": "Password reset successfully. You can now log in."}