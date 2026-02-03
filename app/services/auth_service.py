from datetime import datetime, timedelta
from typing import Optional

from jose import jwt, JWTError
from sqlalchemy.orm import Session
import bcrypt
import logging

from models.user import User
from schemas.user import UserCreate, UserLogin
from core.config import settings
from core.exceptions import (
    DuplicateException,
    UnauthorizedException,
    NotFoundException
)

logger = logging.getLogger(__name__)


# ========================================
# PASSWORD HASHING
# ========================================
def hash_password(password: str) -> str:
    """Hash password with bcrypt"""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify password against hash"""
    password_bytes = password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")
    return bcrypt.checkpw(password_bytes, hashed_bytes)


# ========================================
# JWT TOKEN
# ========================================
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token"""
    to_encode = data.copy()

    # Token expiration time
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})

    # Create token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        raise UnauthorizedException("Invalid token")


# ========================================
# AUTH LOGIC
# ========================================
def register_user(db: Session, user_data: UserCreate) -> User:
    """Register new user"""

    # Check if email exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_data.email}")
        raise DuplicateException(f"Email {user_data.email} already registered")

    # Hash password
    hashed_password = hash_password(user_data.password)

    # Create user
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    logger.info(f"User registered: {db_user.email}")
    return db_user


def login_user(db: Session, login_data: UserLogin) -> dict:
    """Login and return token"""

    # Find user by email
    db_user = db.query(User).filter(User.email == login_data.email).first()

    # Check user exists and password is correct
    if not db_user or not verify_password(login_data.password, db_user.hashed_password):
        logger.warning(f"Failed login attempt: {login_data.email}")
        raise UnauthorizedException("Invalid email or password")

    # Check if user is active
    if not db_user.is_active:
        raise UnauthorizedException("User is disabled")

    # Create token
    token_data = {"sub": db_user.email, "id": db_user.id}
    access_token = create_access_token(data=token_data)

    logger.info(f"User logged in: {db_user.email}")

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


def get_current_user(db: Session, token: str) -> User:
    """Get current user from token"""

    # Decode token
    payload = decode_access_token(token)
    email: str = payload.get("sub")

    if not email:
        raise UnauthorizedException("Invalid token")

    # Find user
    db_user = db.query(User).filter(User.email == email).first()

    if not db_user:
        raise UnauthorizedException("User not found")

    return db_user