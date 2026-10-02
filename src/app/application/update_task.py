"""Caso de uso: actualizar parcialmente una tarea, sin tocar el estado
(C2, C3)."""

from uuid import UUID

from app.application.common import get_task_or_raise
from app.domain.enums import Priority
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.sentinels import UNSET, _Unset
from app.domain.task import Task


class UpdateTask:
    def __init__(
        self,
        task_list_repository: TaskListRepository,
        task_repository: TaskRepository,
    ) -> None:
        self.task_list_repository = task_list_repository
        self.task_repository = task_repository

    def execute(
        self,
        list_id: UUID,
        task_id: UUID,
        title: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
        priority: Priority | _Unset = UNSET,
    ) -> Task:
        task = get_task_or_raise(
            self.task_list_repository, self.task_repository, list_id, task_id
        )
        task.update(title=title, description=description, priority=priority)
        self.task_repository.update(task)
        return task
