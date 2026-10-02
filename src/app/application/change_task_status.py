"""Caso de uso: cambiar el estado de una tarea (B2, C3)."""

from uuid import UUID

from app.application.common import get_task_or_raise
from app.domain.enums import TaskStatus
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.task import Task


class ChangeTaskStatus:
    def __init__(
        self,
        task_list_repository: TaskListRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository

    def execute(self, list_id: UUID, task_id: UUID, status: TaskStatus) -> Task:
        task = get_task_or_raise(
            self.task_list_repository, self.task_repository, list_id, task_id
        )
        # Stub temporal: todavía no cambia el estado ni persiste
        # (rojo pendiente de GREEN).
        return task
