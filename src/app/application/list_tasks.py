"""Caso de uso: listar las tareas de una lista, con filtros (C4),
paginación (C5), orden por created_at (C6, delegado al repositorio) y
el porcentaje de completitud global de la lista (C7, C8: ignora los
filtros aplicados a items/total)."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.application.page import TaskPage
from app.domain.enums import Priority, TaskStatus
from app.domain.repositories import TaskListRepository, TaskRepository


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
    ) -> TaskPage:
        get_task_list_or_raise(self.task_list_repository, list_id)
        items = self.task_repository.list_by_list(
            list_id, limit=limit, offset=offset, status=status, priority=priority
        )
        total = self.task_repository.count_by_list(
            list_id, status=status, priority=priority
        )
        # Stub temporal: completion_percentage fijo en 0.0, ignora los
        # conteos reales (rojo pendiente de GREEN).
        return TaskPage(
            items=items,
            total=total,
            limit=limit,
            offset=offset,
            completion_percentage=0.0,
        )
