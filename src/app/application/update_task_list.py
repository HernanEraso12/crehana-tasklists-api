"""Caso de uso: actualizar parcialmente una lista de tareas (C2)."""

from uuid import UUID

from app.domain.exceptions import TaskListNotFoundError
from app.domain.repositories import TaskListRepository
from app.domain.sentinels import UNSET, _Unset
from app.domain.task_list import TaskList


class UpdateTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(
        self,
        list_id: UUID,
        name: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
    ) -> TaskList:
        """Stub temporal: busca la lista pero no aplica los cambios ni
        persiste todavía (rojo pendiente de GREEN)."""
        task_list = self.repository.get(list_id)
        if task_list is None:
            raise TaskListNotFoundError(list_id)
        return task_list
