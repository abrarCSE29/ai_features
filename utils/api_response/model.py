"""Pydantic models for standardized API responses."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class SuccessResponse(BaseModel):
    """Standard success response model."""
    
    success: bool = True
    status_code: int = 200
    message: Optional[str] = None
    data: Optional[Any] = None


class ErrorResponse(BaseModel):
    """Standard error response model."""
    
    success: bool = False
    status_code: int = 400
    error_code: str = "ERROR"
    message: str
    details: Optional[Dict[str, Any]] = None


class ValidationError(BaseModel):
    """Validation error details."""
    
    field: str = Field(..., alias="loc")
    message: str
    type: str


class ValidationErrorResponse(BaseModel):
    """Validation error response model."""
    
    success: bool = False
    status_code: int = 422
    error_code: str = "VALIDATION_ERROR"
    message: str = "Validation failed"
    errors: List[ValidationError]
