from sqlalchemy import update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app_project.models.models import Tasks, Status
from app_project.database import session_context


class ConsumerRepository:

    async def get_task_and_check_cancelled(self, session: AsyncSession, task_id: int) -> None:
        task = await session.get(Tasks, task_id)
        if task.status == Status.CANCELLED:
            raise Exception(f"Task {task_id} cancelled")

    async def update_to_in_progress(self, session: AsyncSession, task_id: int) -> None:
        stmt = (
            update(Tasks)
            .where(Tasks.id == task_id)
            .values(started_at=func.timezone('utc', func.now()))
        )

        update_stmt = (
            update(Tasks)
            .where(Tasks.id == task_id)
            .values(status=Status.IN_PROGRESS)
        )

        await session.execute(stmt)
        await session.execute(update_stmt)
        await session.commit()

    async def update_to_completed(self, session: AsyncSession, task_id: int) -> None:
        completed_stmt = (
            update(Tasks)
            .where(Tasks.id == task_id)
            .values(
                status=Status.COMPLETED,
                result={"message": "successfully"},
                completed_at=func.timezone('utc', func.now())
            )
        )

        await session.execute(completed_stmt)
        await session.commit()

    async def update_to_failed(self, task_id: int, error: Exception = None) -> None:
        async with session_context() as session:
            update_stmt = (
                update(Tasks)
                .where(Tasks.id == task_id)
                .values(status=Status.FAILED, errors=str(error) if error else None)
            )
            await session.execute(update_stmt)
            await session.commit()
