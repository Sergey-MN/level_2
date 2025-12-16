from fastapi import Request
from fastapi.responses import JSONResponse
from app_project.exceptions import AppError
import logging

logger = logging.getLogger(__name__)


async def handle_app_error(request: Request, exc: AppError):
    if exc.status_code >= 500:
        logger.error(f"DB Error: {exc.message}")
    else:
        logger.warning(f"Client error: {exc.message}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code.value,
            "message": exc.message,
            "details": exc.details if exc.details else None
        }
    )


async def handle_any_error(request: Request, exc: Exception):
    logger.critical(f"Unhandled error: {exc}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_error",
            "message": "Внутренняя ошибка сервера"
        }
    )


__all__ = ("handle_app_error", "handle_any_error")