"""
Custom exceptions for the application.
"""
from fastapi import HTTPException, status
from typing import Any, Dict, Optional


class BaseAPIException(HTTPException):
    """Base exception class for API errors"""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail, headers=headers)


# ========================================
# NOT FOUND EXCEPTIONS
# ========================================
class NotFoundException(BaseAPIException):
    """Base class for not found exceptions"""
    
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail
        )


class PostNotFoundException(NotFoundException):
    """Raised when a post is not found"""
    
    def __init__(self, post_id: int):
        super().__init__(detail=f"Post with id {post_id} not found")


class UserNotFoundException(NotFoundException):
    """Raised when a user is not found"""
    
    def __init__(self, user_id: int):
        super().__init__(detail=f"User with id {user_id} not found")


# ========================================
# VALIDATION EXCEPTIONS
# ========================================
class ValidationException(BaseAPIException):
    """Raised when validation fails"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail
        )


class DuplicateException(BaseAPIException):
    """Raised when trying to create duplicate resource"""
    
    def __init__(self, detail: str = "Resource already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail
        )


# ========================================
# DATABASE EXCEPTIONS
# ========================================
class DatabaseException(BaseAPIException):
    """Raised when database operation fails"""
    
    def __init__(self, detail: str = "Database error occurred"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail
        )


class DatabaseConnectionException(DatabaseException):
    """Raised when database connection fails"""
    
    def __init__(self):
        super().__init__(detail="Could not connect to database")


# ========================================
# AUTHENTICATION EXCEPTIONS
# ========================================
class UnauthorizedException(BaseAPIException):
    """Raised when authentication fails"""
    
    def __init__(self, detail: str = "Not authenticated"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"}
        )


class ForbiddenException(BaseAPIException):
    """Raised when user doesn't have permission"""
    
    def __init__(self, detail: str = "Not enough permissions"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail
        )


# ========================================
# BUSINESS LOGIC EXCEPTIONS
# ========================================
class InvalidOperationException(BaseAPIException):
    """Raised when operation is not allowed"""
    
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail
        )