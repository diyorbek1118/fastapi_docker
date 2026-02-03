"""
Error response schemas.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ErrorDetail(BaseModel):
    """Single error detail"""
    
    loc: Optional[List[str]] = Field(None, description="Error location")
    msg: str = Field(..., description="Error message")
    type: str = Field(..., description="Error type")


class ErrorResponse(BaseModel):
    """Standard error response"""
    
    success: bool = Field(False, description="Success status")
    error: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    details: Optional[List[ErrorDetail]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    path: Optional[str] = Field(None, description="Request path")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Post with id 999 not found",
                "error_code": "POST_NOT_FOUND",
                "timestamp": "2024-02-01T10:30:00",
                "path": "/api/v1/posts/999"
            }
        }


class ValidationErrorResponse(BaseModel):
    """Validation error response"""
    
    success: bool = Field(False)
    error: str = Field("Validation error")
    details: List[ErrorDetail]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Validation error",
                "details": [
                    {
                        "loc": ["body", "title"],
                        "msg": "field required",
                        "type": "value_error.missing"
                    }
                ],
                "timestamp": "2024-02-01T10:30:00"
            }
        }