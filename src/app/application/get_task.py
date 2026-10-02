"""Caso de uso: obtener una tarea de una lista por id (B9)."""

from uuid import UUID

from app.application.common import get_task_or_raise
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.task import Task


class GetTask:
    def __init__(
        self,
        task_list_repository: TaskListRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository

    def execute(self, list_id: UUID, task_id: UUID) -> Task:
        return get_task_or_raise(
            self.task_list_repository, self.task_repository, list_id, task_id
        )
