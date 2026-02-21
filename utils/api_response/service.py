"""Helper functions for creating standardized API responses."""

from typing import Any, Dict, List, Optional
from fastapi import Response

from api_response.model import (
    SuccessResponse,
    ErrorResponse,
    ValidationErrorResponse,
)


def success(
    data: Optional[Any] = None,
    message: Optional[str] = None,
    status_code: int = 200,
) -> SuccessResponse:
    """Create a success response.
    
    Args:
        data: Response data
        message: Success message
        status_code: HTTP status code
        
    Returns:
        SuccessResponse model
    """
    return SuccessResponse(
        status_code=status_code,
        message=message,
        data=data,
    )


def created(
    data: Optional[Any] = None,
    message: str = "Resource created successfully",
) -> SuccessResponse:
    """Create a 201 Created response.
    
    Args:
        data: Response data
        message: Success message
        
    Returns:
        SuccessResponse model with status code 201
    """
    return SuccessResponse(
        status_code=201,
        message=message,
        data=data,
    )


def error(
    message: str,
    status_code: int = 400,
    error_code: str = "ERROR",
    details: Optional[Dict[str, Any]] = None,
) -> ErrorResponse:
    """Create an error response.
    
    Args:
        message: Error message
        status_code: HTTP status code
        error_code: Error code identifier
        details: Additional error details
        
    Returns:
        ErrorResponse model
    """
    return ErrorResponse(
        status_code=status_code,
        error_code=error_code,
        message=message,
        details=details,
    )


def not_found(
    message: str = "Resource not found",
    error_code: str = "NOT_FOUND",
) -> ErrorResponse:
    """Create a 404 Not Found response.
    
    Args:
        message: Error message
        error_code: Error code identifier
        
    Returns:
        ErrorResponse model with status code 404
    """
    return ErrorResponse(
        status_code=404,
        error_code=error_code,
        message=message,
    )


def unauthorized(
    message: str = "Unauthorized access",
    error_code: str = "UNAUTHORIZED",
) -> ErrorResponse:
    """Create a 401 Unauthorized response.
    
    Args:
        message: Error message
        error_code: Error code identifier
        
    Returns:
        ErrorResponse model with status code 401
    """
    return ErrorResponse(
        status_code=401,
        error_code=error_code,
        message=message,
    )


def forbidden(
    message: str = "Access forbidden",
    error_code: str = "FORBIDDEN",
) -> ErrorResponse:
    """Create a 403 Forbidden response.
    
    Args:
        message: Error message
        error_code: Error code identifier
        
    Returns:
        ErrorResponse model with status code 403
    """
    return ErrorResponse(
        status_code=403,
        error_code=error_code,
        message=message,
    )


def validation_error(
    message: str = "Validation failed",
    errors: Optional[List[Dict[str, Any]]] = None,
) -> ValidationErrorResponse:
    """Create a 422 Validation Error response.
    
    Args:
        message: Error message
        errors: List of validation errors
        
    Returns:
        ValidationErrorResponse model with status code 422
    """
    return ValidationErrorResponse(
        status_code=422,
        error_code="VALIDATION_ERROR",
        message=message,
        errors=errors or [],
    )
