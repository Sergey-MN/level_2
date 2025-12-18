from datetime import datetime
from unittest.mock import AsyncMock

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app_project.api.v1.dependencies import get_task_service
from app_project.main import app
from app_project.models.models import Status, Priority
from app_project.schemas.task_schema import TaskReadSchema


@pytest_asyncio.fixture
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def task_read_schema():
    return TaskReadSchema(id=1, title="Название таски", description="какое-то описание таски",
                          created_at=datetime.now(), priority=Priority.LOW,
                          status=Status.NEW, started_at=None, completed_at=None, result=None,
                          errors=None)


@pytest_asyncio.fixture
async def service_mock(task_read_schema):
    mock = AsyncMock()

    mock.create = AsyncMock(return_value=task_read_schema)
    mock.get_by_id = AsyncMock(return_value=task_read_schema)

    async def override_get_task_service():
        return mock

    app.dependency_overrides[get_task_service] = override_get_task_service
    yield mock
    app.dependency_overrides.clear()


@pytest.fixture
def task_payload():
    return {"title": "Название таски", "description": "какое-то описание таски", "priority": Priority.LOW,
            "status": Status.NEW}
