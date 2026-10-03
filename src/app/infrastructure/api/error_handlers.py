"""Mapea excepciones de dominio y de validación a la respuesta de
error única (C9): {"error": {"code", "message", "details"}}. Las
excepciones de dominio no conocen HTTP (`CLAUDE.md`); este es el
único lugar que las traduce a códigos HTTP."""

from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.domain.exceptions import (
    InvalidCompletionCountsError,
    InvalidTaskError,
    InvalidTaskListError,
    TaskListNotFoundError,
    TaskNotFoundError,
)


def _error_response(
    status_code: int, code: str, message: str, details: Any = None
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message, "details": details}},
    )


async def _handle_task_list_not_found(
    _request: Request, exc: TaskListNotFoundError
) -> JSONResponse:
    return _error_response(status.HTTP_404_NOT_FOUND, "TASK_LIST_NOT_FOUND", str(exc))


async def _handle_task_not_found(
    _request: Request, exc: TaskNotFoundError
) -> JSONResponse:
    return _error_response(status.HTTP_404_NOT_FOUND, "TASK_NOT_FOUND", str(exc))


async def _handle_invalid_domain_value(
    _request: Request, exc: Exception
) -> JSONResponse:
    """InvalidTaskListError, InvalidTaskError, InvalidCompletionCountsError:
    reglas de negocio del dominio (B5, B6, C8), no de los schemas."""
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT, "VALIDATION_ERROR", str(exc)
    )


async def _handle_validation_error(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return _error_response(
        status.HTTP_422_UNPROCESSABLE_CONTENT,
        "VALIDATION_ERROR",
        "Error de validación.",
        details=jsonable_encoder(exc.errors()),
    )


async def _handle_internal_error(_request: Request, _exc: Exception) -> JSONResponse:
    return _error_response(
        status.HTTP_500_INTERNAL_SERVER_ERROR, "INTERNAL_ERROR", "Error interno."
    )


def register_error_handlers(app: FastAPI) -> None:
    app.add_exception_handler(TaskListNotFoundError, _handle_task_list_not_found)
    app.add_exception_handler(TaskNotFoundError, _handle_task_not_found)
    app.add_exception_handler(InvalidTaskListError, _handle_invalid_domain_value)
    app.add_exception_handler(InvalidTaskError, _handle_invalid_domain_value)
    app.add_exception_handler(
        InvalidCompletionCountsError, _handle_invalid_domain_value
    )
    app.add_exception_handler(RequestValidationError, _handle_validation_error)
    app.add_exception_handler(Exception, _handle_internal_error)
