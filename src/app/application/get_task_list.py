"""Caso de uso: obtener una lista de tareas por id."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class GetTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, list_id: UUID) -> TaskList:
        return get_task_list_or_raise(self.repository, list_id)
