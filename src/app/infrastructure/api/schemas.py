"""Schemas Pydantic de la API de listas. Solo tipado y presencia de
campos (y la regla propia de la API, C2: el PATCH exige al menos un
campo). El recorte, la longitud y el vacío del nombre los valida el
dominio (`TaskList`, B5), que ya los aplica: no se duplican aquí.
`InvalidTaskListError` se mapea a 422 en `error_handlers.py`."""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, model_validator

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
            raise ValueError("Debe enviar al menos un campo para actualizar.")
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
