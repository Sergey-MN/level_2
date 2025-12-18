from datetime import datetime
from unittest.mock import AsyncMock

import pytest

from app_project.models.models import Status
from tests.unit.conftest import client


@pytest.mark.asyncio
async def test_create_task(client, service_mock, task_payload):
    response = await client.post("/api/v1/tasks/", json=task_payload)

    assert response.status_code == 201
    assert response.json().get("title") == task_payload.get("title")
    assert response.json().get("description") == task_payload.get("description")
    assert response.json().get("id") == 1
    assert response.json().get("created_at") != None
    assert response.json().get("priority") == task_payload.get("priority")
    assert response.json().get("status") == task_payload.get("status")


@pytest.mark.asyncio
async def test_get_task(client, service_mock, task_payload):
    response = await client.get("/api/v1/tasks/1")

    assert response.status_code == 200
    assert response.json().get("title") == task_payload.get("title")
    assert response.json().get("description") == task_payload.get("description")
    assert response.json().get("id") == 1
    assert response.json().get("created_at") != None
    assert response.json().get("priority") == task_payload.get("priority")
    assert response.json().get("status") == task_payload.get("status")


@pytest.mark.asyncio
@pytest.mark.parametrize("task_id,status,status_from_service", [
    (1, "new", Status.NEW),
    (2, "pending", Status.PENDING),
    (3, "in_progress", Status.IN_PROGRESS),
    (4, "completed", Status.COMPLETED),
    (5, "failed", Status.FAILED),
    (6, "cancelled", Status.CANCELLED),
])
async def test_get_task_status(client, service_mock, task_id, status, status_from_service):
    service_mock.get_status = AsyncMock(return_value=status_from_service)

    response = await client.get(f"/api/v1/tasks/{task_id}/status")

    assert response.status_code == 200
    assert "status" in response.json()
    assert response.json()["status"] == status


@pytest.mark.asyncio
async def test_delete_task(client, service_mock):
    response = await client.delete("/api/v1/tasks/1")

    assert response.status_code == 200
    assert response.json().get("detail") == "deleted"


@pytest.mark.asyncio
async def test_get_list_tasks(client, service_mock):
    mock_tasks = [
        {"id": 1, "title": "Task 1", "description": "description task 1", "status": "new", "created_at": datetime.now(),
         "started_at": None, "completed_at": None, "result": {}, "errors": ""},
        {"id": 2, "title": "Task 2", "description": "description task 2", "status": "pending",
         "created_at": datetime.now(),
         "started_at": None, "completed_at": None, "result": {}, "errors": ""},
        {"id": 3, "title": "Task 2", "description": "description task 3", "status": "in_progress",
         "created_at": datetime.now(),
         "started_at": datetime.now(), "completed_at": None, "result": {}, "errors": ""},
        {"id": 4, "title": "Task 2", "description": "description task 4", "status": "completed",
         "created_at": datetime.now(),
         "started_at": datetime.now(), "completed_at": datetime.now(), "result": {}, "errors": ""},
        {"id": 5, "title": "Task 2", "description": "description task 5", "status": "failed",
         "created_at": datetime.now(),
         "started_at": datetime.now(), "completed_at": datetime.now(), "result": {}, "errors": ""},
        {"id": 6, "title": "Task 2", "description": "description task 6", "status": "cancelled",
         "created_at": datetime.now(),
         "started_at": None, "completed_at": None, "result": {}, "errors": ""}
    ]
    service_mock.get_list = AsyncMock(return_value=mock_tasks)
    response = await client.get("/api/v1/tasks/")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(mock_tasks)
    assert data[0].get("id") == 1
    assert data[0].get("title") == "Task 1"
    assert data[0].get("description") == "description task 1"
    assert data[0].get("status") == "new"
