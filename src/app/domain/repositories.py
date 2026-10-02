"""Puertos de repositorio (A2). `domain` define la interfaz; `infrastructure`
la implementa. Cada `Protocol` solo declara los métodos que sus casos de uso
necesitan: no es un CRUD genérico por adelantado."""

from typing import Protocol
from uuid import UUID

from app.domain.task_list import TaskList


class TaskListRepository(Protocol):
    def add(self, task_list: TaskList) -> None: ...

    def get(self, list_id: UUID) -> TaskList | None: ...

    def list(self, limit: int, offset: int) -> list[TaskList]: ...

    def count(self) -> int: ...

    def update(self, task_list: TaskList) -> None: ...
