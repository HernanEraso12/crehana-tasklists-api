"""Caso de uso: actualizar parcialmente una lista de tareas (C2)."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.domain.repositories import TaskListRepository
from app.domain.sentinels import UNSET, _Unset
from app.domain.task_list import TaskList


class UpdateTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(
        self,
        list_id: UUID,
        name: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
    ) -> TaskList:
        task_list = get_task_list_or_raise(self.repository, list_id)
        task_list.update(name=name, description=description)
        self.repository.update(task_list)
        return task_list
