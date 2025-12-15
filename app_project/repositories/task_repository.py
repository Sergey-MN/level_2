from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app_project.models.models import Tasks, Status
from app_project.schemas.task_schema import TaskCreateSchema, TaskFilter


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: TaskCreateSchema) -> Tasks:
        model = Tasks(**task.model_dump())
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model

    async def filtres_list_paginate(self, filters: TaskFilter, limit: int = 10,
                                    cursor_id: int | None = None) -> Sequence[Tasks]:

        data = filters.model_dump(exclude_none=True)

        conditions = self._build_filters(Tasks, data)

        if cursor_id is not None:
            conditions.append(Tasks.id > cursor_id)

        stmt = (select(Tasks)
                .where(*conditions)
                .limit(limit)
                )

        result = await self.session.scalars(stmt)
        return result.all()

    @staticmethod
    def _build_filters(model, filter_data: dict) -> list:
        conditions = []

        for field, value in filter_data.items():
            if value is not None:
                column = getattr(model, field, None)
                if column is not None:
                    conditions.append(column == value)
        return conditions

    async def get_by_id(self, task_id: int) -> Tasks | None:
        task = await self.session.get(Tasks, task_id)
        return task

    async def delete_by_id(self, task_id: int) -> int | None:
        stmt = delete(Tasks).where(Tasks.id == task_id)
        await self.session.execute(stmt)
        await self.session.commit()
        return task_id

    async def get_status_by_id(self, task_id: int) -> Status | None:
        stmt = select(Tasks.status).where(Tasks.id == task_id)
        status = await self.session.scalar(stmt)
        return status
