"""Request ID middleware for FastAPI."""

import uuid
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from utils.logger.bindings import set_request_id, clear_request_id


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to generate and bind request_id to each request.
    
    Extracts X-Request-ID from header if present, otherwise generates UUID.
    Sets the request_id in the logger context for the duration of the request.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and add request_id to context."""
        # Get request_id from header or generate new one
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set request_id in context for logging
        set_request_id(request_id)
        
        try:
            # Process the request
            response = await call_next(request)
            
            # Add request_id to response headers
            response.headers["X-Request-ID"] = request_id
            
            return response
        finally:
            # Clear request_id from context after request is complete
            clear_request_id()
