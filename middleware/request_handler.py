import logging
from functools import wraps
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def log_request_middleware(func):
    """Middleware decorator that logs incoming requests"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Log request details
        logger.info(f"Request received at {datetime.now().isoformat()}")
        logger.info(f"Function: {func.__name__}")
        logger.info(f"Args: {args}")
        logger.info(f"Kwargs: {kwargs}")
        
        try:
            # Execute the request handler
            result = func(*args, **kwargs)
            logger.info(f"Request completed successfully")
            return result
        except Exception as e:
            logger.error(f"Request failed with error: {str(e)}")
            raise
    
    return wrapper