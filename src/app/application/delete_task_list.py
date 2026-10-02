"""Caso de uso: eliminar una lista de tareas."""

from uuid import UUID

from app.domain.exceptions import TaskListNotFoundError
from app.domain.repositories import TaskListRepository


class DeleteTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, list_id: UUID) -> None:
        task_list = self.repository.get(list_id)
        if task_list is None:
            raise TaskListNotFoundError(list_id)
        # Stub temporal: todavía no borra nada (rojo pendiente de GREEN).
