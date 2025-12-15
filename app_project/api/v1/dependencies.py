from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app_project.database import get_session
from app_project.repositories.task_repository import TaskRepository
from app_project.services.task_service import TaskService


def get_task_service(session: AsyncSession = Depends(get_session)) -> TaskService:
    return TaskService(TaskRepository(session))