"""Caso de uso: eliminar una tarea de una lista."""

from uuid import UUID

from app.application.common import get_task_or_raise
from app.domain.repositories import TaskListRepository, TaskRepository


class DeleteTask:
    def __init__(
        self,
        task_list_repository: TaskListRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository

    def execute(self, list_id: UUID, task_id: UUID) -> None:
        get_task_or_raise(
            self.task_list_repository, self.task_repository, list_id, task_id
        )
        self.task_repository.delete(task_id)
