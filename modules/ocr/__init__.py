"""OCR module for text extraction from documents."""

from .service import OCRService
from .models import OCRTextResponse, ErrorResponse
from .router import router

__all__ = ["OCRService", "OCRTextResponse", "ErrorResponse", "router"]
