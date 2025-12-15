from sqlalchemy import Sequence

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
        lst_tasks = await self.repository.filtres_list_paginate(filters, limit, cursor_id)
        return lst_tasks

    async def get_by_id(self, task_id: int) -> Tasks:
        model = await self.repository.get_by_id(task_id)
        return model

    async def delete_by_id(self, task_id: int) -> None:
        await self.repository.delete_by_id(task_id)

    async def get_status(self, task_id: int) -> Status:
        return await self.repository.get_status_by_id(task_id)
