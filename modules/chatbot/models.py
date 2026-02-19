"""Response models for Chatbot API endpoints."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class ChatRequest(BaseModel):
    """Request model for the chatbot endpoint."""

    message: str = Field(..., description="The message from the user")
    session_id: str = Field(..., description="Unique identifier for the chat session", example="session_123")


class ChatResponse(BaseModel):
    """Response model for the chatbot endpoint."""

    status: str = Field(..., description="Status of the operation", example="success")
    response: str = Field(..., description="The response from the chatbot")
    session_id: str = Field(..., description="The session identifier")


class ErrorResponse(BaseModel):
    """Response model for error responses."""

    status: str = Field(..., description="Status of the operation", example="error")
    message: str = Field(..., description="Error message describing what went wrong")
