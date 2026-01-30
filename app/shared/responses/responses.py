from pydantic import BaseModel
from typing import Any, Optional


class ErrorResponse(BaseModel):
    """Standard error response model"""
    success: bool = False
    error_code: str
    message: str
    details: Optional[Any] = None


class SuccessResponse(BaseModel):
    """Standard success response model"""
    success: bool = True
    data: Any
    message: Optional[str] = None