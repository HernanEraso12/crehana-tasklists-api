"""Endpoint de cambio de estado de una tarea
(`/api/v1/lists/{list_id}/tasks/{task_id}/status`, docs/04-api.md).
Un caso de uso, un endpoint (C3, SRP): el estado no se toca desde el
PATCH general de `routers/tasks.py`."""

from uuid import UUID

from fastapi import APIRouter, Depends

from app.application.change_task_status import ChangeTaskStatus
from app.infrastructure.api.dependencies import get_change_task_status_use_case
from app.infrastructure.api.schemas import TaskResponse, TaskStatusUpdate

router = APIRouter(prefix="/api/v1/lists/{list_id}/tasks", tags=["tasks"])


@router.patch("/{task_id}/status", response_model=TaskResponse)
def change_task_status(
    list_id: UUID,
    task_id: UUID,
    payload: TaskStatusUpdate,
    use_case: ChangeTaskStatus = Depends(get_change_task_status_use_case),
) -> TaskResponse:
    task = use_case.execute(list_id=list_id, task_id=task_id, status=payload.status)
    return TaskResponse.from_domain(task)
