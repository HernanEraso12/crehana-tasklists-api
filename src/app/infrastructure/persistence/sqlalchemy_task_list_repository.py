"""Repositorio TaskListRepository con SQLAlchemy 2.0 síncrono (A2, A5).

Mapea explícitamente entre el modelo ORM y la entidad de dominio: los
modelos ORM no se exponen fuera de `infrastructure/persistence`. No
hace `commit`: el commit lo hace la capa API, una vez por request.
"""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.task_list import TaskList
from app.infrastructure.persistence.models import TaskListModel


def _as_utc(value: datetime) -> datetime:
    """SQLite no conserva el offset de zona horaria: lo que vuelve es
    naive pero representa la misma hora UTC que se guardó. Si ya trae
    tzinfo (p. ej. Postgres), se normaliza a UTC en vez de asumir."""
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _to_domain(model: TaskListModel) -> TaskList:
    return TaskList(
        name=model.name,
        description=model.description,
        id=UUID(model.id),
        created_at=_as_utc(model.created_at),
        updated_at=_as_utc(model.updated_at),
    )


def _to_model(task_list: TaskList) -> TaskListModel:
    return TaskListModel(
        id=str(task_list.id),
        name=task_list.name,
        description=task_list.description,
        created_at=task_list.created_at,
        updated_at=task_list.updated_at,
    )


class SqlAlchemyTaskListRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task_list: TaskList) -> None:
        self.session.add(_to_model(task_list))
        self.session.flush()

    def get(self, list_id: UUID) -> TaskList | None:
        model = self.session.get(TaskListModel, str(list_id))
        return _to_domain(model) if model is not None else None

    def list(self, limit: int, offset: int) -> list[TaskList]:
        stmt = (
            select(TaskListModel)
            .order_by(TaskListModel.created_at)
            .limit(limit)
            .offset(offset)
        )
        models = self.session.scalars(stmt).all()
        return [_to_domain(model) for model in models]

    def count(self) -> int:
        stmt = select(func.count()).select_from(TaskListModel)
        return self.session.scalar(stmt) or 0

    def update(self, task_list: TaskList) -> None:
        model = self.session.get(TaskListModel, str(task_list.id))
        if model is None:
            return
        model.name = task_list.name
        model.description = task_list.description
        model.updated_at = task_list.updated_at
        self.session.flush()

    def delete(self, list_id: UUID) -> None:
        model = self.session.get(TaskListModel, str(list_id))
        if model is not None:
            self.session.delete(model)
            self.session.flush()
