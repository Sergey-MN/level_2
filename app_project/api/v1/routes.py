from fastapi import APIRouter
from fastapi.params import Depends

from app_project.api.v1.dependencies import get_task_service
from app_project.schemas.task_schema import TaskCreateSchema, TaskFilter, TaskReadSchema, TaskStatusResponse
from app_project.services.task_service import TaskService

router = APIRouter(prefix="/api/v1/tasks",
                   tags=["tasks"])


@router.post("/", response_model=TaskReadSchema, status_code=201)
async def create_task(task: TaskCreateSchema, service: TaskService = Depends(get_task_service)):
    obj = await service.create(task)
    return TaskReadSchema.model_validate(obj)


@router.get("/", response_model=list[TaskReadSchema], status_code=200)
async def get_list_tasks(filters: TaskFilter, limit: int = 10, cursor_id: int | None = None,
                         service: TaskService = Depends(get_task_service)):
    lst_tasks = await service.get_list(filters, limit, cursor_id)
    return [TaskReadSchema.model_validate(t) for t in lst_tasks]


@router.get("/{task_id}", response_model=TaskReadSchema, status_code=200)
async def get_task(task_id: int, service: TaskService = Depends(get_task_service)):
    obj = await service.get_by_id(task_id)
    return TaskReadSchema.model_validate(obj)


@router.delete("/{task_id}", status_code=200)
async def delete_task(task_id: int, service: TaskService = Depends(get_task_service)):
    await service.delete_by_id(task_id)
    return {"detail": "deleted"}


@router.get("/{task_id}/status", response_model=TaskStatusResponse, status_code=200)
async def get_task_status(task_id: int, service: TaskService = Depends(get_task_service)):
    return TaskStatusResponse(status=await service.get_status(task_id))
