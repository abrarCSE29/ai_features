"""Bindings for request_id context variable."""

from contextvars import ContextVar
from typing import Optional

# Context variable to store request_id for the current request
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)


def get_request_id() -> Optional[str]:
    """Get the current request_id from context."""
    return request_id_var.get()


def set_request_id(request_id: str) -> None:
    """Set the request_id in context."""
    request_id_var.set(request_id)


def clear_request_id() -> None:
    """Clear the request_id from context."""
    request_id_var.set(None)
