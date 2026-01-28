"""Router for OCR service endpoints."""

from typing import Optional, Union
from fastapi import APIRouter, UploadFile, File

from .service import OCRService
from .models import OCRTextResponse, ErrorResponse

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post(
    "/extract-text",
    response_model=Union[OCRTextResponse, ErrorResponse],
)
async def extract_text_from_pdf(file: Optional[UploadFile] = File(None)):
    """
    Extract text from an uploaded PDF file.

    Args:
        file: PDF file uploaded by the client

    Returns:
        Dictionary containing the extracted text
    """
    try:
        # Check if file is provided
        if file is None:
            return {"status": "error", "message": "No file provided. Please upload a PDF file."}
        
        # Check if file is empty
        if file.filename == "":
            return {"status": "error", "message": "File is empty. Please upload a valid PDF file."}
        
        content = await file.read()
        
        # Check if content is empty
        if not content:
            return {"status": "error", "message": "File content is empty. Please upload a valid PDF file."}
        
        extracted_text = OCRService.extract_text_from_file(content)
        return {
            "status": "success",
            "filename": file.filename,
            "text": extracted_text,
        }
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
