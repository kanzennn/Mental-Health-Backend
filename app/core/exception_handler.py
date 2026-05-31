import json
import logging
import traceback

from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from app.utils.response import ResponseBuilder

logger = logging.getLogger(__name__)


def setup_exception_handler(app):

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=ResponseBuilder.error(message=str(exc.detail)),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        serializable_errors = json.loads(json.dumps(exc.errors(), default=str))
        return JSONResponse(
            status_code=422,
            content=ResponseBuilder.error(message="Validation error", errors=serializable_errors),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled error: {str(exc)}")
        logger.error(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content=ResponseBuilder.error(errors=str(exc)),
        )
