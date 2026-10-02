"""Caso de uso: crear una tarea dentro de una lista."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.domain.enums import Priority
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.task import Task


class CreateTask:
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
        title: str,
        description: str | None = None,
        priority: Priority = Priority.MEDIUM,
    ) -> Task:
        get_task_list_or_raise(self.task_list_repository, list_id)
        task = Task(
            title=title,
            list_id=list_id,
            description=description,
            priority=priority,
        )
        self.task_repository.add(task)
        return task
