"""Exception handler middleware for logging validation errors."""

from typing import Callable

from fastapi import Request, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

from utils.logger.logger import logger


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware to log validation errors and HTTP exceptions."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process the request and log any validation errors."""
        try:
            response = await call_next(request)
            return response
        except RequestValidationError as exc:
            # Log validation errors
            logger.error(
                "Request validation error",
                path=request.url.path,
                method=request.method,
                errors=exc.errors(),
                body=exc.body,
            )
            raise
        except HTTPException as exc:
            # Log HTTP exceptions
            logger.error(
                "HTTP exception",
                path=request.url.path,
                method=request.method,
                status_code=exc.status_code,
                detail=exc.detail,
            )
            raise
        except Exception as exc:
            # Log unexpected exceptions
            logger.error(
                "Unexpected error",
                path=request.url.path,
                method=request.method,
                error=str(exc),
            )
            raise
