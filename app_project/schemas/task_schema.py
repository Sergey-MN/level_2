from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app_project.models.models import Priority, Status


class TaskCreateSchema(BaseModel):
    """Схема для создания новой задачи"""

    title: str = Field(min_length=1, max_length=50, examples=["Обработка данных"], description="Название задачи",
                       json_schema_extra={"x-order": 1})
    description: str = Field(min_length=1, max_length=500, examples=["Пример с данными"],
                             description="Данные для обработки", json_schema_extra={"x-order": 2})
    priority: Priority = Field(default=Priority.LOW,
                               examples=[Priority.LOW, Priority.MEDIUM, Priority.HIGH],
                               description="Приоритет выполнения", json_schema_extra={"x-order": 3,
                                                                                      "x-queue-mapping": {
                                                                                          "HIGH": "tasks.high",
                                                                                          "MEDIUM": "tasks.medium",
                                                                                          "LOW": "tasks.low"
                                                                                      }
                                                                                      })
    status: Status = Field(default=Status.NEW,
                           examples=[Status.NEW, Status.PENDING, Status.COMPLETED, Status.CANCELLED, Status.FAILED,
                                     Status.IN_PROGRESS],
                           json_schema_extra={"x-order": 4,
                                              "x-status-flow": "NEW → PENDING → IN_PROGRESS → COMPLETED/FAILED/CANCELLED"})


class TaskReadSchema(TaskCreateSchema, BaseModel):
    """Схема ответа с полной информацией о задаче"""

    id: int = Field(examples=[42], description="ID задачи", json_schema_extra={"x-order": 0})
    created_at: datetime = Field(examples=["2025-12-12T23:59:59Z"], description="Дата и время создания задачи (UTC)",
                                 json_schema_extra={
                                     "x-order": 5,
                                     "format": "date-time",
                                     "readOnly": True
                                 })
    started_at: Optional[datetime] = Field(examples=["2025-12-12T23:59:59Z"],
                                           description="Дата и время начала выполнения задачи (UTC)",
                                           json_schema_extra={
                                               "x-order": 6,
                                               "format": "date-time",
                                               "readOnly": True
                                           })
    completed_at: Optional[datetime] = Field(examples=["2025-12-12T23:59:59Z"],
                                             description="Дата и время завершения выпонения задачи (UTC)",
                                             json_schema_extra={
                                                 "x-order": 7,
                                                 "format": "date-time",
                                                 "readOnly": True
                                             })
    result: Optional[dict] = Field(default=None, examples=[{"message": "result"}], description="Результат выполнения",
                                   json_schema_extra={
                                       "x-order": 8,
                                       "readOnly": True
                                   })
    errors: Optional[str] = Field(default=None, examples=["Unexpected error: ..."],
                                  description="Информация об ошибках",
                                  json_schema_extra={
                                      "x-order": 9,
                                      "readOnly": True,
                                      "format": "text"
                                  }
                                  )

    model_config = ConfigDict(from_attributes=True)


class TaskFilter(BaseModel):
    """Схема для получения списка задач с фильтрацией и пагинацией"""

    title: Optional[str] = Field(default=None, examples=["Отчет"],
                                 description="Фильтр по названию задачи (частичное совпадение)")
    priority: Optional[Priority] = Field(default=None, examples=[Priority.LOW, Priority.MEDIUM, Priority.HIGH],
                                         description="Фильтр по приоритету задачи")
    status: Optional[Status] = Field(default=None, examples=[Priority.LOW, Priority.MEDIUM, Priority.HIGH],
                                     description="Фильтр по статусу задачи")
    created_at: Optional[datetime] = Field(default=None, examples=["2025-12-12T23:59:59Z"],
                                           description="Дата и время создания задачи (UTC)")
    started_at: Optional[datetime] = Field(default=None, examples=["2025-12-12T23:59:59Z"],
                                           description="Дата и время начала выпонения задачи (UTC)")
    completed_at: Optional[datetime] = Field(default=None, examples=["2025-12-12T23:59:59Z"],
                                             description="Дата и время завершения выпонения задачи (UTC)")


class TaskStatusResponse(BaseModel):
    """Схема ответа статуса задачи"""

    status: Status = Field(default=Status.NEW,
                           examples=[Status.NEW, Status.PENDING, Status.COMPLETED, Status.CANCELLED, Status.FAILED,
                                     Status.IN_PROGRESS],
                           json_schema_extra={"x-order": 1,
                                              "x-status-flow": "NEW → PENDING → IN_PROGRESS → COMPLETED/FAILED/CANCELLED"})
