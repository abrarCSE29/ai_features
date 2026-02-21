"""Models for OCR API endpoints."""

# No module-specific request/response models needed.
# Responses use the shared utils/api_response models (SuccessResponse, ErrorResponse).
# OCR data is returned in the `data` field of SuccessResponse:
#   { "filename": "...", "text": "..." }
