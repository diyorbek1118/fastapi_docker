from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from core.dependencies import get_db, get_authenticated_user
from schemas.user import UserCreate, UserLogin, UserResponse, TokenResponse
from services.auth_service import register_user, login_user
from models.user import User

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register new user"
)
def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """Register a new user"""
    return register_user(db=db, user_data=user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login"
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """Login and get token"""
    return login_user(db=db, login_data=login_data)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user"
)
def get_me(
    current_user: User = Depends(get_authenticated_user)
):
    """Get current authenticated user"""
    return current_user