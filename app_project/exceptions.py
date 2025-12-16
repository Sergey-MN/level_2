# exceptions.py
from typing import Optional, Dict, Any
from enum import Enum


class ErrorCode(Enum):
    NOT_FOUND = "not_found"
    ALREADY_EXISTS = "already_exists"
    VALIDATION_ERROR = "validation_error"
    DATABASE_ERROR = "database_error"
    INTEGRITY_ERROR = "integrity_error"


class AppError(Exception):

    def __init__(self, message: str, code: ErrorCode = ErrorCode.DATABASE_ERROR, status_code: int = 400,
                 details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class RepositoryError(AppError):
    pass


class NotFoundError(RepositoryError):

    def __init__(self, model: str = None, object_id: Any = None):
        if model and object_id is not None:
            message = f"{model} с ID {object_id} не найден"
        elif model:
            message = f"{model} не найден"
        else:
            message = "Объект не найден"

        super().__init__(message=message, code=ErrorCode.NOT_FOUND, status_code=404,
                         details={"model": model, "id": object_id} if model else {})


class AlreadyExistsError(RepositoryError):

    def __init__(self, model: str = None, field: str = None, value: Any = None):
        if model and field and value is not None:
            message = f"{model} с {field}={value} уже существует"
        else:
            message = "Объект уже существует"

        super().__init__(message=message, code=ErrorCode.ALREADY_EXISTS, status_code=409,
                         details={"model": model, "field": field, "value": value})


class DatabaseError(RepositoryError):

    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message=message, code=ErrorCode.DATABASE_ERROR, status_code=500)


class ServiceError(AppError):

    def __init__(self, message: str, code: str = "business_error", details: dict | None = None):
        super().__init__(message=message, code=ErrorCode.VALIDATION_ERROR, status_code=400,
                         details={"business_code": code})


class ValidationError(ServiceError):

    def __init__(self, message: str, field: str = None, value: Any = None):
        details = {"field": field} if field else {}
        if value is not None:
            details["value"] = value

        super().__init__(message=message, code="validation_error", details=details)
