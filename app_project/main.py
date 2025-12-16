from fastapi import FastAPI

from app_project.api.v1.routes import router
from app_project.error_handler import handle_app_error, handle_any_error
from app_project.exceptions import AppError

app = FastAPI(
    title="Task processing API",
    description="Асинхронный сервис обработки задач",
    version="1.0.0",

    summary="Обработка задач через RabbitMQ",

    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

app.add_exception_handler(AppError, handle_app_error)
app.add_exception_handler(Exception, handle_any_error)


app.include_router(router)

