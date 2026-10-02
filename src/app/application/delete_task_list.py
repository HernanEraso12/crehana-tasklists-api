"""Caso de uso: eliminar una lista de tareas."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.domain.repositories import TaskListRepository


class DeleteTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, list_id: UUID) -> None:
        get_task_list_or_raise(self.repository, list_id)
        self.repository.delete(list_id)
