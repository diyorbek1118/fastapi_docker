from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


# Register uchun (input)
class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None


# Login uchun (input)
class UserLogin(BaseModel):
    email: EmailStr
    password: str


# Response (output) - password ko'rsatilmaydi!
class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# Token response
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"