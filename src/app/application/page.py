"""Página de resultados paginados (C5), reutilizable entre casos de uso
de listado (listas, tareas)."""

from dataclasses import dataclass
from typing import Generic, TypeVar

from app.domain.task import Task

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


@dataclass
class TaskPage(Page[Task]):
    """Página de tareas con el porcentaje de completitud global de la
    lista (C7, C8): ignora los filtros aplicados a `items`/`total`."""

    completion_percentage: float
