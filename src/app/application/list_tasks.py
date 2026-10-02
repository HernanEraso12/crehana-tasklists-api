"""Caso de uso: listar las tareas de una lista, con filtros (C4) y
paginación (C5), ordenadas por created_at (C6, delegado al repositorio).
El porcentaje de completitud no es parte de este caso de uso."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.application.page import Page
from app.domain.enums import Priority, TaskStatus
from app.domain.repositories import TaskListRepository, TaskRepository
from app.domain.task import Task


class ListTasks:
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
        limit: int,
        offset: int,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> Page[Task]:
        get_task_list_or_raise(self.task_list_repository, list_id)
        items = self.task_repository.list_by_list(
            list_id, limit=limit, offset=offset, status=status, priority=priority
        )
        total = self.task_repository.count_by_list(
            list_id, status=status, priority=priority
        )
        return Page(items=items, total=total, limit=limit, offset=offset)
