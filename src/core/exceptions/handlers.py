import logging

from fastapi import Request
from fastapi.responses import JSONResponse

from src.core.exceptions.exceptions import AppException
from src.utils.colored_console import console;


logger = logging.getLogger(__name__)


async def app_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:

    if not isinstance(exc, AppException):
        # This should never happen because this handler is registered
        # specifically for AppException.
        logger.error(
            "Unexpected exception received by AppException handler",
            exc_info=exc,
        )

        console.print(exc, style="bold red");

        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Internal server error",
                },
            },
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.error_code,
                "message": exc.message,
            },
        },
    )


async def generic_exception_handler(
    request: Request,
    exc: Exception,
):
    # IMPORTANT:
    # Log the actual exception internally.
    logger.exception(
        "Unhandled exception: %s %s",
        request.method,
        request.url.path,
    )

    # Don't expose internal exception details to the client.
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
            },
        },
    )