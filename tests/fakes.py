"""Repositorios fake en memoria para tests de casos de uso (D2).
Nunca mocks: implementaciones reales y simples que cumplen los puertos
definidos en `app.domain.repositories`.

Guardan y devuelven copias (`copy.deepcopy`), no la referencia que
recibieron: así se comportan como una BD real, donde mutar la entidad
en memoria no persiste nada hasta llamar a `add`/`update`, y lo que se
lee de vuelta es una instancia distinta a la que se guardó."""

from copy import deepcopy
from uuid import UUID

from app.domain.task import Task
from app.domain.task_list import TaskList


class InMemoryTaskListRepository:
    def __init__(self) -> None:
        self.lists: dict[UUID, TaskList] = {}

    def add(self, task_list: TaskList) -> None:
        self.lists[task_list.id] = deepcopy(task_list)

    def get(self, list_id: UUID) -> TaskList | None:
        task_list = self.lists.get(list_id)
        return deepcopy(task_list) if task_list is not None else None

    def list(self, limit: int, offset: int) -> list[TaskList]:
        ordered = sorted(self.lists.values(), key=lambda tl: tl.created_at)
        return [deepcopy(tl) for tl in ordered[offset : offset + limit]]

    def count(self) -> int:
        return len(self.lists)

    def update(self, task_list: TaskList) -> None:
        self.lists[task_list.id] = deepcopy(task_list)

    def delete(self, list_id: UUID) -> None:
        self.lists.pop(list_id, None)


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self.tasks: dict[UUID, Task] = {}

    def add(self, task: Task) -> None:
        self.tasks[task.id] = deepcopy(task)

    def get(self, task_id: UUID) -> Task | None:
        task = self.tasks.get(task_id)
        return deepcopy(task) if task is not None else None

    def update(self, task: Task) -> None:
        self.tasks[task.id] = deepcopy(task)
