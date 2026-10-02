"""Repositorios fake en memoria para tests de casos de uso (D2).
Nunca mocks: implementaciones reales y simples que cumplen los puertos
definidos en `app.domain.repositories`."""

from uuid import UUID

from app.domain.task_list import TaskList


class InMemoryTaskListRepository:
    def __init__(self) -> None:
        self.lists: dict[UUID, TaskList] = {}

    def add(self, task_list: TaskList) -> None:
        self.lists[task_list.id] = task_list

    def get(self, list_id: UUID) -> TaskList | None:
        return self.lists.get(list_id)

    def list(self, limit: int, offset: int) -> list[TaskList]:
        ordered = sorted(self.lists.values(), key=lambda tl: tl.created_at)
        return ordered[offset : offset + limit]

    def count(self) -> int:
        return len(self.lists)
