"""Caso de uso: obtener una lista de tareas por id."""

from uuid import UUID

from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class GetTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, list_id: UUID) -> TaskList:
        """Stub temporal: devuelve lo que diga el repositorio, incluido
        None, sin lanzar TaskListNotFoundError (rojo pendiente de GREEN)."""
        return self.repository.get(list_id)
