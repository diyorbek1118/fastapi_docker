from fastapi import APIRouter, Depends, status, Request
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address

from core.dependencies import get_db, get_authenticated_user
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from services.auth_service import register_user, login_user, create_access_token
from models.user import User

# Rate limiter
limiter = Limiter(key_func=get_remote_address)

router = APIRouter(prefix="/auth", tags=["Auth"])


# ========================================
# REGISTER (Rate limit: 3/minute)
# ========================================

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
@limiter.limit("3/minute")
def register(
    request: Request,
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register - 3 requests per minute"""
    db_user = register_user(db=db, user_data=user_data)
    token_data = {"sub": db_user.email, "id": db_user.id}
    access_token = create_access_token(data=token_data)
    return {"access_token": access_token, "token_type": "bearer"}


# ========================================
# LOGIN (Rate limit: 5/minute)
# ========================================
@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login"
)
@limiter.limit("5/minute")
def login(
    request: Request,
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login - 5 requests per minute"""
    return login_user(db=db, login_data=login_data)


# ========================================
# ME (No rate limit)
# ========================================
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user"
)
def get_me(
    current_user: User = Depends(get_authenticated_user)
):
    """Get current user - No limit"""
    return current_user