"""Helpers compartidos entre casos de uso."""

from uuid import UUID

from app.domain.exceptions import TaskListNotFoundError
from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


def get_task_list_or_raise(repository: TaskListRepository, list_id: UUID) -> TaskList:
    """Obtiene la lista o lanza TaskListNotFoundError. Usado por los
    casos de uso que necesitan la lista existente antes de operar."""
    task_list = repository.get(list_id)
    if task_list is None:
        raise TaskListNotFoundError(list_id)
    return task_list
