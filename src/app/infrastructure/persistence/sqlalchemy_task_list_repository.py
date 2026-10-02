"""Repositorio TaskListRepository con SQLAlchemy 2.0 síncrono (A2, A5).

Mapea explícitamente entre el modelo ORM y la entidad de dominio: los
modelos ORM no se exponen fuera de `infrastructure/persistence`. No
hace `commit`: el commit lo hace la capa API, una vez por request.
"""

from uuid import UUID

from sqlalchemy.orm import Session

from app.domain.task_list import TaskList


class SqlAlchemyTaskListRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task_list: TaskList) -> None:
        """Stub temporal: no persiste nada todavía (rojo pendiente de
        GREEN; los modelos ORM y database.py se agregan en esa fase)."""

    def get(self, list_id: UUID) -> TaskList | None:
        """Stub temporal: siempre devuelve None."""
        return None

    def list(self, limit: int, offset: int) -> list[TaskList]:
        """Stub temporal: siempre devuelve una lista vacía."""
        return []

    def count(self) -> int:
        """Stub temporal: siempre devuelve 0."""
        return 0

    def update(self, task_list: TaskList) -> None:
        """Stub temporal: no hace nada."""

    def delete(self, list_id: UUID) -> None:
        """Stub temporal: no hace nada."""
