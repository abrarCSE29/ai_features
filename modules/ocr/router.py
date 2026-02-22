"""Router for OCR service endpoints."""

from typing import Union
from fastapi import APIRouter, UploadFile, File

from .service import OCRService
from utils.api_response.service import success, error
from utils.api_response.model import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/ocr", tags=["ocr"])


@router.post(
    "/extract-text",
    response_model=Union[SuccessResponse, ErrorResponse],
)
async def extract_text_from_pdf(file: UploadFile = File(...)):
    """
    Extract text from an uploaded PDF file.
    """
    if not file.filename:
        return error(
            message="No file provided. Please upload a PDF file.",
            status_code=400,
            error_code="NO_FILE",
        )

    content = await file.read()

    if not content:
        return error(
            message="File content is empty. Please upload a valid PDF file.",
            status_code=400,
            error_code="EMPTY_FILE",
        )

    try:
        extracted_text = OCRService.extract_text_from_file(content)
        return success(
            data={"filename": file.filename, "text": extracted_text},
            message="Text extracted successfully",
        )
    except ValueError as e:
        return error(message=str(e), status_code=422, error_code="OCR_ERROR")
    except Exception as e:
        return error(
            message=f"Unexpected error: {str(e)}",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
