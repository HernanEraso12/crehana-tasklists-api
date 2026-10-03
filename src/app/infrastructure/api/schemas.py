"""Schemas Pydantic de la API (listas y tareas). Solo tipado,
presencia de campos y reglas propias de la API (C2: el PATCH exige al
menos un campo; C3: el PATCH de tareas no acepta `status`, `extra`
`forbid`). El recorte, la longitud y el vacío del nombre/título los
valida el dominio (`TaskList` B5, `Task` B6), que ya los aplica: no se
duplican aquí. `InvalidTaskListError`/`InvalidTaskError` se mapean a
422 en `error_handlers.py`."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, model_validator

from app.domain.enums import Priority, TaskStatus
from app.domain.task import Task
from app.domain.task_list import TaskList


class TaskListCreate(BaseModel):
    name: str
    description: str | None = None


class TaskListUpdate(BaseModel):
    name: str | None = None
    description: str | None = None

    @model_validator(mode="after")
    def _at_least_one_field(self) -> "TaskListUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update.")
        return self

    def to_use_case_kwargs(self) -> dict[str, Any]:
        """Solo los campos que el cliente envió (UNSET implícito para
        el resto): `exclude_unset` distingue "no enviado" de
        "enviado como null", igual que el sentinel UNSET del dominio."""
        return self.model_dump(exclude_unset=True)


class TaskListResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task_list: TaskList) -> "TaskListResponse":
        return cls(
            id=task_list.id,
            name=task_list.name,
            description=task_list.description,
            created_at=task_list.created_at,
            updated_at=task_list.updated_at,
        )


class TaskListPageResponse(BaseModel):
    items: list[TaskListResponse]
    total: int
    limit: int
    offset: int


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: Priority = Priority.MEDIUM


class TaskUpdate(BaseModel):
    # extra="forbid" (C3): un campo status aquí debe rechazarse, no
    # ignorarse. El estado solo se cambia por su propio endpoint.
    model_config = ConfigDict(extra="forbid")

    title: str | None = None
    description: str | None = None
    priority: Priority | None = None

    @model_validator(mode="after")
    def _at_least_one_field(self) -> "TaskUpdate":
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided for update.")
        return self

    def to_use_case_kwargs(self) -> dict[str, Any]:
        return self.model_dump(exclude_unset=True)


class TaskStatusUpdate(BaseModel):
    # extra="forbid": un PATCH .../status solo cambia el estado (C3);
    # cualquier otro campo en el body se rechaza.
    model_config = ConfigDict(extra="forbid")

    status: TaskStatus


class TaskResponse(BaseModel):
    id: UUID
    list_id: UUID
    title: str
    description: str | None
    priority: Priority
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, task: Task) -> "TaskResponse":
        return cls(
            id=task.id,
            list_id=task.list_id,
            title=task.title,
            description=task.description,
            priority=task.priority,
            status=task.status,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )


class TaskPageResponse(BaseModel):
    items: list[TaskResponse]
    total: int
    limit: int
    offset: int
    completion_percentage: float
