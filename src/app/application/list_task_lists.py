"""Caso de uso: listar listas de tareas con paginación (C5) y orden por
created_at ascendente (C6, delegado al repositorio)."""

from app.application.page import Page
from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class ListTaskLists:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, limit: int, offset: int) -> Page[TaskList]:
        """Stub temporal: siempre devuelve una página vacía fija
        (rojo pendiente de GREEN)."""
        return Page(items=[], total=0, limit=limit, offset=offset)
