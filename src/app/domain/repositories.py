"""Puertos de repositorio (A2). `domain` define la interfaz; `infrastructure`
la implementa. Cada `Protocol` solo declara los métodos que sus casos de uso
necesitan: no es un CRUD genérico por adelantado."""

from typing import Protocol
from uuid import UUID

from app.domain.enums import Priority, TaskStatus
from app.domain.task import Task
from app.domain.task_list import TaskList


class TaskListRepository(Protocol):
    def add(self, task_list: TaskList) -> None: ...

    def get(self, list_id: UUID) -> TaskList | None: ...

    def list(self, limit: int, offset: int) -> list[TaskList]: ...

    def count(self) -> int: ...

    def update(self, task_list: TaskList) -> None: ...

    def delete(self, list_id: UUID) -> None: ...


class TaskRepository(Protocol):
    def add(self, task: Task) -> None: ...

    def get(self, task_id: UUID) -> Task | None: ...

    def update(self, task: Task) -> None: ...

    def delete(self, task_id: UUID) -> None: ...

    def list_by_list(
        self,
        list_id: UUID,
        limit: int,
        offset: int,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[Task]: ...

    def count_by_list(
        self,
        list_id: UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> int: ...

    def completion_counts(self, list_id: UUID) -> tuple[int, int]:
        """Devuelve (completadas, totales) de toda la lista, sin
        filtros (C8). Pensado para resolverse con una agregación SQL
        en la implementación real; aquí solo es la interfaz."""
        ...
