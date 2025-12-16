from typing import Sequence

from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app_project.exceptions import AlreadyExistsError, DatabaseError, NotFoundError
from app_project.models.models import Tasks, Status
from app_project.schemas.task_schema import TaskCreateSchema, TaskFilter


class TaskRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, task: TaskCreateSchema) -> Tasks:
        try:
            model = Tasks(**task.model_dump())
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)
            return model

        except IntegrityError as e:
            await self.session.rollback()
            raise AlreadyExistsError(model="Tasks", field="description", value=e.args[0])

        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Не удалось создать задачу: {str(e)}")

    async def filtres_list_paginate(self, filters: TaskFilter, limit: int = 10,
                                    cursor_id: int | None = None) -> Sequence[Tasks]:
        try:
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

        except SQLAlchemyError as e:
            raise DatabaseError(f"Не удалось получить список задач: {str(e)}")

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
        try:
            task = await self.session.get(Tasks, task_id)
            if not task:
                raise NotFoundError(object_id=task_id)
            return task

        except SQLAlchemyError as e:
            raise DatabaseError(f"Не удалось получить задачу {task_id}: {str(e)}")

    async def delete_by_id(self, task_id: int) -> int | None:
        try:
            task = await self.get_by_id(task_id)

            stmt = delete(Tasks).where(Tasks.id == task_id)
            result = await self.session.execute(stmt)
            await self.session.commit()
            return True


        except SQLAlchemyError as e:
            await self.session.rollback()
            raise DatabaseError(f"Не удалось удалить задачу {task_id}: {str(e)}")

    async def get_status_by_id(self, task_id: int) -> Status | None:
        task = await self.get_by_id(task_id)
        return task.status
