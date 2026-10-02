"""Caso de uso: obtener una lista de tareas por id."""

from uuid import UUID

from app.domain.exceptions import TaskListNotFoundError
from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class GetTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, list_id: UUID) -> TaskList:
        task_list = self.repository.get(list_id)
        if task_list is None:
            raise TaskListNotFoundError(list_id)
        return task_list
