"""Router for Chatbot service endpoints."""

from typing import Union
from fastapi import APIRouter

from .chatbot_service import chatbot_service
from .models import ChatRequest
from utils.api_response.service import success, error
from utils.api_response.model import SuccessResponse, ErrorResponse

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post(
    "/chat",
    response_model=Union[SuccessResponse, ErrorResponse],
)
async def chat_with_bot(request: ChatRequest):
    """
    Interact with the chatbot.
    """
    try:
        response_text = await chatbot_service.generate_response(
            message=request.message,
            session_id=request.session_id
        )
        return success(
            data={"bot_response": response_text, "session_id": request.session_id},
            message="Response generated successfully",
        )
    except ValueError as e:
        return error(message=str(e), status_code=400, error_code="CHATBOT_ERROR")
    except Exception as e:
        return error(message=f"Unexpected error: {str(e)}", status_code=500, error_code="INTERNAL_ERROR")
