"""Helpers compartidos entre casos de uso."""

from uuid import UUID

from app.domain.exceptions import TaskListNotFoundError, TaskNotFoundError
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.task import Task
from app.domain.task_list import TaskList


def get_task_list_or_raise(repository: TaskListRepository, list_id: UUID) -> TaskList:
    """Obtiene la lista o lanza TaskListNotFoundError. Usado por los
    casos de uso que necesitan la lista existente antes de operar."""
    task_list = repository.get(list_id)
    if task_list is None:
        raise TaskListNotFoundError(list_id)
    return task_list


def get_task_or_raise(
    task_list_repository: TaskListRepository,
    task_repository: TaskRepository,
    list_id: UUID,
    task_id: UUID,
) -> Task:
    """Verifica primero que la lista exista (TaskListNotFoundError), y
    luego obtiene la tarea o lanza TaskNotFoundError(task_id) si no
    existe o si existe en otra lista (B9: no se revela que existe en
    otra). Reutilizable para obtener, actualizar, cambiar estado y
    eliminar tareas."""
    get_task_list_or_raise(task_list_repository, list_id)
    task = task_repository.get(task_id)
    if task is None or task.list_id != list_id:
        raise TaskNotFoundError(task_id)
    return task
