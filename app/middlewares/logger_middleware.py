import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)


async def log_request_middleware(request: Request, call_next):
    start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.url}")

    response = await call_next(request)

    process_time = time.time() - start_time
    logger.info(
        f"Completed: {request.method} {request.url} "
        f"in {process_time:.4f}s"
    )
    return response
