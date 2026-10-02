"""Caso de uso: listar listas de tareas con paginación (C5) y orden por
created_at ascendente (C6, delegado al repositorio)."""

from app.application.page import Page
from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class ListTaskLists:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, limit: int, offset: int) -> Page[TaskList]:
        items = self.repository.list(limit=limit, offset=offset)
        total = self.repository.count()
        return Page(items=items, total=total, limit=limit, offset=offset)
