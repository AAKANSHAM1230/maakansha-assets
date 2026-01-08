import time
from functools import wraps
from src.utils.logger import get_logger

logger = get_logger("RetryPolicy")

def with_retry(max_retries=3, delay=1):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            attempts = 0
            while attempts < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempts += 1
                    logger.warning(f"Error: {e}. Retrying ({attempts}/{max_retries})...")
                    time.sleep(delay)
            
            logger.error(f"Operation failed after {max_retries} attempts.")
            raise Exception(f"Failed after {max_retries} retries")
        return wrapper
    return decorator