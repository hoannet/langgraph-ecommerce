"""Retry decorator for handling rate limits and transient errors."""

import time
import functools
from typing import Callable, Any
from src.core.logging import get_logger

logger = get_logger(__name__)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    max_delay: float = 60.0,
):
    """
    Retry decorator with exponential backoff for rate limits.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
        backoff_factor: Multiplier for delay after each retry
        max_delay: Maximum delay between retries
        
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e)
                    
                    # Check if it's a rate limit error
                    is_rate_limit = (
                        "429" in error_str or
                        "RESOURCE_EXHAUSTED" in error_str or
                        "quota" in error_str.lower() or
                        "rate limit" in error_str.lower()
                    )
                    
                    if not is_rate_limit or attempt >= max_retries:
                        # Not a rate limit or max retries reached
                        raise
                    
                    # Extract retry delay from error if available
                    retry_delay = delay
                    if "retry in" in error_str.lower():
                        try:
                            # Extract delay like "5.611376018s"
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                            if match:
                                retry_delay = float(match.group(1))
                                logger.info(f"Using API suggested retry delay: {retry_delay}s")
                        except:
                            pass
                    
                    # Cap at max_delay
                    retry_delay = min(retry_delay, max_delay)
                    
                    logger.warning(
                        f"⏳ Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {retry_delay:.1f}s..."
                    )
                    
                    await asyncio.sleep(retry_delay)
                    
                    # Exponential backoff for next attempt
                    delay = min(delay * backoff_factor, max_delay)
            
            # All retries exhausted
            logger.error(f"❌ All {max_retries} retries exhausted")
            raise last_exception
        
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    error_str = str(e)
                    
                    # Check if it's a rate limit error
                    is_rate_limit = (
                        "429" in error_str or
                        "RESOURCE_EXHAUSTED" in error_str or
                        "quota" in error_str.lower() or
                        "rate limit" in error_str.lower()
                    )
                    
                    if not is_rate_limit or attempt >= max_retries:
                        raise
                    
                    # Extract retry delay from error if available
                    retry_delay = delay
                    if "retry in" in error_str.lower():
                        try:
                            import re
                            match = re.search(r'retry in ([\d.]+)s', error_str.lower())
                            if match:
                                retry_delay = float(match.group(1))
                                logger.info(f"Using API suggested retry delay: {retry_delay}s")
                        except:
                            pass
                    
                    retry_delay = min(retry_delay, max_delay)
                    
                    logger.warning(
                        f"⏳ Rate limit hit (attempt {attempt + 1}/{max_retries}). "
                        f"Retrying in {retry_delay:.1f}s..."
                    )
                    
                    time.sleep(retry_delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            logger.error(f"❌ All {max_retries} retries exhausted")
            raise last_exception
        
        # Return appropriate wrapper based on function type
        import asyncio
        import inspect
        if inspect.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
