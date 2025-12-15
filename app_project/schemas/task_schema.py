from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, ConfigDict

from app_project.models.models import Priority, Status


class TaskCreateSchema(BaseModel):
    title: str = Field(max_length=50)
    description: str
    priority: Priority = Priority.LOW
    status: Status = Status.NEW


class TaskReadSchema(TaskCreateSchema, BaseModel):
    id: int
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    result: Optional[dict]
    errors: Optional[str]

    model_config = ConfigDict(from_attributes=True)


class TaskFilter(BaseModel):
    title: Optional[str]
    description: Optional[str]
    priority: Optional[Priority]
    status: Optional[Status]
    created_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class TaskStatusResponse(BaseModel):
    status: str
