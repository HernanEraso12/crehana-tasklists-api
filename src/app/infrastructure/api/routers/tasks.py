"""Endpoints de tareas (`/api/v1/lists/{list_id}/tasks`, docs/04-api.md).
Sin lógica de negocio ni consultas: cada handler llama a un caso de
uso (`CLAUDE.md`). El cambio de estado y el listado filtrado tienen
sus propios ciclos; no viven aquí."""

from uuid import UUID

from fastapi import APIRouter, Depends, Response, status

from app.application.create_task import CreateTask
from app.application.delete_task import DeleteTask
from app.application.get_task import GetTask
from app.application.update_task import UpdateTask
from app.infrastructure.api.dependencies import (
    get_create_task_use_case,
    get_delete_task_use_case,
    get_get_task_use_case,
    get_update_task_use_case,
)
from app.infrastructure.api.schemas import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/v1/lists/{list_id}/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    list_id: UUID,
    payload: TaskCreate,
    response: Response,
    use_case: CreateTask = Depends(get_create_task_use_case),
) -> TaskResponse:
    task = use_case.execute(
        list_id=list_id,
        title=payload.title,
        description=payload.description,
        priority=payload.priority,
    )
    response.headers["Location"] = f"/api/v1/lists/{list_id}/tasks/{task.id}"
    return TaskResponse.from_domain(task)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    list_id: UUID,
    task_id: UUID,
    use_case: GetTask = Depends(get_get_task_use_case),
) -> TaskResponse:
    return TaskResponse.from_domain(use_case.execute(list_id=list_id, task_id=task_id))


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
    list_id: UUID,
    task_id: UUID,
    payload: TaskUpdate,
    use_case: UpdateTask = Depends(get_update_task_use_case),
) -> TaskResponse:
    task = use_case.execute(
        list_id=list_id, task_id=task_id, **payload.to_use_case_kwargs()
    )
    return TaskResponse.from_domain(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(
    list_id: UUID,
    task_id: UUID,
    use_case: DeleteTask = Depends(get_delete_task_use_case),
) -> None:
    use_case.execute(list_id=list_id, task_id=task_id)
