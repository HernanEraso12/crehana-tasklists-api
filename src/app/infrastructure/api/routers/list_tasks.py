"""Endpoint de listado de tareas con filtros, paginación y
completitud (`GET /api/v1/lists/{list_id}/tasks`, C4, C5, C7, C8,
docs/04-api.md). Separado de `routers/tasks.py` igual que el cambio
de estado: es su propio ciclo."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query

from app.application.list_tasks import ListTasks
from app.domain.enums import Priority, TaskStatus
from app.infrastructure.api.dependencies import get_list_tasks_use_case
from app.infrastructure.api.schemas import TaskPageResponse, TaskResponse

router = APIRouter(prefix="/api/v1/lists/{list_id}/tasks", tags=["tasks"])


@router.get("", response_model=TaskPageResponse)
def list_tasks(
    list_id: UUID,
    status: TaskStatus | None = Query(default=None),
    priority: Priority | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    use_case: ListTasks = Depends(get_list_tasks_use_case),
) -> TaskPageResponse:
    page = use_case.execute(
        list_id=list_id,
        limit=limit,
        offset=offset,
        status=status,
        priority=priority,
    )
    return TaskPageResponse(
        items=[TaskResponse.from_domain(task) for task in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
        completion_percentage=page.completion_percentage,
    )
