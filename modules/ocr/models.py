"""Response models for OCR API endpoints."""

from pydantic import BaseModel, Field


class OCRTextResponse(BaseModel):
    """Response model for text extraction endpoint."""

    status: str = Field(..., description="Status of the operation", example="success")
    filename: str = Field(..., description="Name of the uploaded file")
    text: str = Field(..., description="Extracted text from the document")


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    status: str = Field(..., description="Status of the operation", example="error")
    message: str = Field(..., description="Error message describing what went wrong")
