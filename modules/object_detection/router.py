import json
from typing import Union
from fastapi import APIRouter, UploadFile, File, Form

from utils.logger.logger import Logger
from .service import ObjectDetectionService
from utils.api_response.service import success, error
from utils.api_response.model import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/object-detection", tags=["object-detection"])
logger = Logger()


@router.post(
    "/detect",
    response_model=Union[SuccessResponse, ErrorResponse],
)
async def detect_objects(
    file: UploadFile = File(...),
    object_names: str = Form(...),
    threshold: float = Form(0.25),
):
    logger.info("Received Request at /detect")
    # Parse object_names (JSON string or comma-separated)
    try:
        parsed_names = json.loads(object_names)
        if not isinstance(parsed_names, list):
            parsed_names = [str(parsed_names)]
    except json.JSONDecodeError:
        parsed_names = [
            name.strip() for name in object_names.split(",") if name.strip()
        ]

    if not parsed_names:
        return error(
            message="list should not be empty", status_code=400, error_code="EMPTY_LIST"
        )

    if not file.filename:
        return error(message="No file provided.", status_code=400, error_code="NO_FILE")

    content = await file.read()
    if not content:
        return error(
            message="File content is empty.", status_code=400, error_code="EMPTY_FILE"
        )

    try:
        result = ObjectDetectionService.detect(content, parsed_names, threshold)
        total_count = sum(d.count for d in result.detections.values())
        return success(
            data=result.model_dump(),
            message="Objects detected successfully" if total_count > 0 else "No objects detected",
        )
    except ValueError as e:
        return error(message=str(e), status_code=422, error_code="DETECTION_ERROR")
    except Exception as e:
        return error(
            message=f"Unexpected error: {str(e)}",
            status_code=500,
            error_code="INTERNAL_ERROR",
        )
