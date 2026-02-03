from fastapi import Depends, Header
from typing import Optional
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.user import User
from services.auth_service import get_current_user


# ========================================
# DATABASE
# ========================================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ========================================
# AUTH DEPENDENCY
# ========================================
def get_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract token from Authorization header"""
    if not authorization:
        from core.exceptions import UnauthorizedException
        raise UnauthorizedException("No token provided")

    # "Bearer <token>" → "<token>"
    try:
        token = authorization.split(" ")[1]
    except IndexError:
        from core.exceptions import UnauthorizedException
        raise UnauthorizedException("Invalid token format")

    return token


def get_authenticated_user(
    token: str = Depends(get_token),
    db: Session = Depends(get_db)
) -> User:
    """Get authenticated user from token"""
    return get_current_user(db=db, token=token)