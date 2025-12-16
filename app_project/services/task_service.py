from sqlalchemy import Sequence

from app_project.exceptions import ValidationError, ServiceError
from app_project.models.models import Tasks, Status
from app_project.repositories.task_repository import TaskRepository
from app_project.schemas.task_schema import TaskCreateSchema, TaskFilter


class TaskService:
    def __init__(self, repository: TaskRepository):
        self.repository = repository

    async def create(self, task: TaskCreateSchema) -> Tasks:
        model = await self.repository.create(task)
        return model

    async def get_list(self, filters: TaskFilter, limit: int, cursor_id: int | None) -> Sequence[Tasks]:

        if limit < 1 or limit > 50:
            raise ValidationError(message="Лимит должен быть от 1 до 50", field="limit", value=limit)

        if cursor_id is not None and cursor_id < 0:
            raise ValidationError(message="Cursor ID не может быть отрицательным", field="cursor_id", value=cursor_id)

        lst_tasks = await self.repository.filtres_list_paginate(filters, limit, cursor_id)
        return lst_tasks

    async def get_by_id(self, task_id: int) -> Tasks:
        if task_id <= 0:
            raise ValidationError(message="ID задачи должен быть положительным числом", field="task_id", value=task_id)

        model = await self.repository.get_by_id(task_id)
        return model

    async def delete_by_id(self, task_id: int) -> None:
        if task_id <= 0:
            raise ValidationError(message="ID задачи должен быть положительным числом", field="task_id", value=task_id)

        task = await self.repository.get_by_id(task_id)

        if task.status == Status.COMPLETED:
            raise ServiceError(message="Нельзя удалить завершенную задачу", code="CANNOT_DELETE_COMPLETED")

        await self.repository.delete_by_id(task_id)

    async def get_status(self, task_id: int) -> Status:

        if task_id <= 0:
            raise ValidationError(
                message="ID задачи должен быть положительным числом",
                field="task_id",
                value=task_id
            )

        return await self.repository.get_status_by_id(task_id)
