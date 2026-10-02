"""Caso de uso: crear una lista de tareas."""

from app.domain.repositories import TaskListRepository
from app.domain.task_list import TaskList


class CreateTaskList:
    def __init__(self, repository: TaskListRepository) -> None:
        self.repository = repository

    def execute(self, name: str, description: str | None = None) -> TaskList:
        """Stub temporal: crea la entidad pero no la persiste todavía
        (rojo pendiente de GREEN)."""
        return TaskList(name=name, description=description)
