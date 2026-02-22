"""Request model for Chatbot API endpoints."""

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Request model for the chatbot endpoint."""

    message: str = Field(..., description="The message from the user")
    session_id: str = Field(
        ..., description="Unique identifier for the chat session", example="session_123"
    )
