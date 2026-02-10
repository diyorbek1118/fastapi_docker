from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.user import User
from services.auth_service import get_current_user

security = HTTPBearer()


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
def get_authenticated_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get authenticated user from token"""
    token = credentials.credentials
    return get_current_user(db=db, token=token)
