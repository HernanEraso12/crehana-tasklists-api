"""Página de resultados paginados (C5), reutilizable entre casos de uso
de listado (listas, tareas)."""

from dataclasses import dataclass
from typing import Generic, TypeVar

T = TypeVar("T")


@dataclass
class Page(Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int
