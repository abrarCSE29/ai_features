"""Router for Chatbot service endpoints."""

from typing import Union
from fastapi import APIRouter, HTTPException

from .chatbot_service import chatbot_service
from .models import ChatRequest, ChatResponse, ErrorResponse

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.post(
    "/chat",
    response_model=Union[ChatResponse, ErrorResponse],
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

        return {
            "status": "success",
            "response": response_text,
            "session_id": request.session_id
        }
    except ValueError as e:
        return {"status": "error", "message": str(e)}
    except Exception as e:
        return {"status": "error", "message": f"Unexpected error: {str(e)}"}
