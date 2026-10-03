"""Endpoints de listas de tareas (`/api/v1/lists`, docs/04-api.md).
Sin lógica de negocio ni consultas: cada handler llama a un caso de
uso (`CLAUDE.md`)."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status

from app.application.create_task_list import CreateTaskList
from app.application.delete_task_list import DeleteTaskList
from app.application.get_task_list import GetTaskList
from app.application.list_task_lists import ListTaskLists
from app.application.update_task_list import UpdateTaskList
from app.infrastructure.api.dependencies import (
    get_create_task_list_use_case,
    get_delete_task_list_use_case,
    get_get_task_list_use_case,
    get_list_task_lists_use_case,
    get_update_task_list_use_case,
)
from app.infrastructure.api.schemas import (
    TaskListCreate,
    TaskListPageResponse,
    TaskListResponse,
    TaskListUpdate,
)

router = APIRouter(prefix="/api/v1", tags=["lists"])


@router.post(
    "/lists", response_model=TaskListResponse, status_code=status.HTTP_201_CREATED
)
def create_task_list(
    payload: TaskListCreate,
    response: Response,
    use_case: CreateTaskList = Depends(get_create_task_list_use_case),
) -> TaskListResponse:
    task_list = use_case.execute(name=payload.name, description=payload.description)
    response.headers["Location"] = f"/api/v1/lists/{task_list.id}"
    return TaskListResponse.from_domain(task_list)


@router.get("/lists", response_model=TaskListPageResponse)
def list_task_lists(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    use_case: ListTaskLists = Depends(get_list_task_lists_use_case),
) -> TaskListPageResponse:
    page = use_case.execute(limit=limit, offset=offset)
    return TaskListPageResponse(
        items=[TaskListResponse.from_domain(task_list) for task_list in page.items],
        total=page.total,
        limit=page.limit,
        offset=page.offset,
    )


@router.get("/lists/{list_id}", response_model=TaskListResponse)
def get_task_list(
    list_id: UUID,
    use_case: GetTaskList = Depends(get_get_task_list_use_case),
) -> TaskListResponse:
    return TaskListResponse.from_domain(use_case.execute(list_id=list_id))


@router.patch("/lists/{list_id}", response_model=TaskListResponse)
def update_task_list(
    list_id: UUID,
    payload: TaskListUpdate,
    use_case: UpdateTaskList = Depends(get_update_task_list_use_case),
) -> TaskListResponse:
    task_list = use_case.execute(list_id=list_id, **payload.to_use_case_kwargs())
    return TaskListResponse.from_domain(task_list)


@router.delete("/lists/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task_list(
    list_id: UUID,
    use_case: DeleteTaskList = Depends(get_delete_task_list_use_case),
) -> None:
    use_case.execute(list_id=list_id)
