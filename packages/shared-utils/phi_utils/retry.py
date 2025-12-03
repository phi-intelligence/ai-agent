"""
Retry utilities for LLM calls and local agent communication
"""
import asyncio
from typing import Callable, TypeVar, Optional, List
from functools import wraps
import logging

T = TypeVar('T')

logger = logging.getLogger(__name__)


async def retry_async(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> T:
    """
    Retry an async function with exponential backoff
    
    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay on each retry
        exceptions: Tuple of exceptions to catch and retry
        logger: Optional logger for retry attempts
    """
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return await func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                if logger:
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {current_delay}s: {str(e)}"
                    )
                await asyncio.sleep(current_delay)
                current_delay *= backoff
            else:
                if logger:
                    logger.error(f"Max retries ({max_retries}) exceeded: {str(e)}")
                raise
    
    raise last_exception


def retry_sync(
    func: Callable[..., T],
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger: Optional[logging.Logger] = None
) -> T:
    """
    Retry a sync function with exponential backoff
    """
    import time
    last_exception = None
    current_delay = delay
    
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exception = e
            if attempt < max_retries:
                if logger:
                    logger.warning(
                        f"Retry attempt {attempt + 1}/{max_retries} after {current_delay}s: {str(e)}"
                    )
                time.sleep(current_delay)
                current_delay *= backoff
            else:
                if logger:
                    logger.error(f"Max retries ({max_retries}) exceeded: {str(e)}")
                raise
    
    raise last_exception


