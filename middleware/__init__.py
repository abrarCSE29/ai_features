"""Middleware package for FastAPI application."""

from fastapi import FastAPI

from middleware.request_id_middleware import RequestIDMiddleware


def register_middleware(app: FastAPI) -> None:
    """Register all middleware for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Add request ID middleware
    app.add_middleware(RequestIDMiddleware)
