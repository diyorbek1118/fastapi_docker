from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from sqlalchemy.orm import Session

from core.database import SessionLocal
from models.user import User
from services.auth_service import get_current_user

# ========================================
# ASYNC IMPORTS (YANGI!)
# ========================================
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import SessionLocal, AsyncSessionLocal
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
# ASYNC DATABASE (YANGI! - Posts uchun)
# ========================================
async def get_async_db():
    """
    Async database session.
    
    Usage:
        @router.get("/posts/")
        async def get_posts(db: AsyncSession = Depends(get_async_db)):
            ...
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


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
