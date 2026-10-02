"""Repositorio TaskRepository con SQLAlchemy 2.0 síncrono (A2, A5).

Mapea explícitamente entre el modelo ORM y la entidad de dominio: los
modelos ORM no se exponen fuera de `infrastructure/persistence`. No
hace `commit`: el commit lo hace la capa API, una vez por request.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.enums import Priority, TaskStatus
from app.domain.task import Task


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task: Task) -> None:
        """Stub temporal: no persiste nada todavía (rojo pendiente de
        GREEN; el modelo ORM se agrega en esa fase)."""

    def get(self, task_id: UUID) -> Task | None:
        """Stub temporal: siempre devuelve None."""
        return None

    def update(self, task: Task) -> None:
        """Stub temporal: no hace nada."""

    def delete(self, task_id: UUID) -> None:
        """Stub temporal: no hace nada."""

    def list_by_list(
        self,
        list_id: UUID,
        limit: int,
        offset: int,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[Task]:
        """Stub temporal: siempre devuelve una lista vacía."""
        return []

    def count_by_list(
        self,
        list_id: UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> int:
        """Stub temporal: siempre devuelve 0."""
        return 0

    def completion_counts(self, list_id: UUID) -> tuple[int, int]:
        """Stub temporal: siempre devuelve (0, 0)."""
        return (0, 0)
