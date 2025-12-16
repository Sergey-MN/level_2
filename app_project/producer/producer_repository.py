from sqlalchemy import select, update

from app_project.models.models import Tasks, Status


class ProducerRepository:
    async def get_new_tasks(self, session) -> list:
        stmt = select(Tasks).where(Tasks.status == Status.NEW)
        result = await session.execute(stmt)
        return result.scalars().all()

    async def update_status_to_pending(self, session, task_ids: list):
        update_stmt = (
            update(Tasks)
            .where(Tasks.id.in_(task_ids))
            .values(status=Status.PENDING)
        )

        await session.execute(update_stmt)
        await session.commit()
