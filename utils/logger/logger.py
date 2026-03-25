"""Logger class using structlog for structured logging."""

import threading
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path
from typing import Any, Optional

import structlog

from utils.logger.bindings import get_request_id


class Logger:
    """Thread-safe logger class using structlog.
    
    Features:
    - Log levels: info, warning, error, debug
    - Thread-safe operations using threading.Lock
    - File output to logs/ folder
    - Daily rotation at midnight (00:00)
    - Filename format: ai-features-YYYY-MM-DD.log
    - Request_id binding from context
    """

    _instance: Optional["Logger"] = None
    _lock = threading.Lock()

    def __new__(cls) -> "Logger":
        """Singleton pattern to ensure single logger instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        """Initialize the logger."""
        if self._initialized:
            return

        self._initialized = True
        self._file_lock = threading.Lock()
        
        # Configuration
        self._project_name = "ai-features"
        self._log_dir = Path("logs")
        self._log_dir.mkdir(exist_ok=True)
        
        # Setup structlog
        self._setup_structlog()

    def _get_log_filename(self) -> str:
        """Get the log filename with current date."""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"{self._project_name}-{today}.log"

    def _setup_structlog(self) -> None:
        """Setup structlog with processors and handlers."""
        # Create log file path
        log_file = self._log_dir / self._get_log_filename()
        
        # Ensure log directory exists
        self._log_dir.mkdir(parents=True, exist_ok=True)
        
        # Create file handler with midnight rotation
        file_handler = TimedRotatingFileHandler(
            filename=str(log_file),
            when="midnight",
            interval=1,
            backupCount=0,  # Keep all log files
            encoding="utf-8"
        )
        file_handler.suffix = "%Y-%m-%d"
        # Removed incorrect rotate call - handled by TimedRotatingFileHandler
        
        # Define processors for structlog
        processors = [
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            self._add_request_id,
            structlog.processors.JSONRenderer(),
        ]

        # Configure structlog
        structlog.configure(
            processors=processors,
            wrapper_class=structlog.stdlib.BoundLogger,
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )

        # Get the root logger and add our handlers
        structlog.get_logger()
        
        # Add file handler to standard library logger
        stdlib_logger = structlog.stdlib.get_logger()
        stdlib_logger.handlers = []
        stdlib_logger.addHandler(file_handler)
        stdlib_logger.setLevel("INFO")

    def _add_request_id(self, logger: Any, method_name: str, event_dict: dict) -> dict:
        """Add request_id to log event if available in context."""
        request_id = get_request_id()
        if request_id:
            event_dict["request_id"] = request_id
        return event_dict

    def _log(self, level: str, message: str, **kwargs: Any) -> None:
        """Internal log method with thread safety."""
        with self._file_lock:
            log_func = getattr(structlog.get_logger(), level)
            log_func(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log info level message."""
        self._log("info", message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log warning level message."""
        self._log("warning", message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log error level message."""
        self._log("error", message, **kwargs)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log debug level message."""
        self._log("debug", message, **kwargs)


# Singleton instance
logger = Logger()
