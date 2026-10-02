"""Repositorio TaskRepository con SQLAlchemy 2.0 síncrono (A2, A5).

Mapea explícitamente entre el modelo ORM y la entidad de dominio: los
modelos ORM no se exponen fuera de `infrastructure/persistence`. No
hace `commit`: el commit lo hace la capa API, una vez por request.
"""

from uuid import UUID

from sqlalchemy import case, func, select
from sqlalchemy.orm import Session

from app.domain.enums import Priority, TaskStatus
from app.domain.task import Task
from app.infrastructure.persistence.models import TaskModel
from app.infrastructure.persistence.timestamps import as_utc


def _to_domain(model: TaskModel) -> Task:
    return Task(
        title=model.title,
        list_id=UUID(model.list_id),
        description=model.description,
        priority=Priority(model.priority),
        status=TaskStatus(model.status),
        id=UUID(model.id),
        created_at=as_utc(model.created_at),
        updated_at=as_utc(model.updated_at),
    )


def _to_model(task: Task) -> TaskModel:
    return TaskModel(
        id=str(task.id),
        list_id=str(task.list_id),
        title=task.title,
        description=task.description,
        priority=task.priority.value,
        status=task.status.value,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


class SqlAlchemyTaskRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def add(self, task: Task) -> None:
        self.session.add(_to_model(task))
        self.session.flush()

    def get(self, task_id: UUID) -> Task | None:
        model = self.session.get(TaskModel, str(task_id))
        return _to_domain(model) if model is not None else None

    def update(self, task: Task) -> None:
        model = self.session.get(TaskModel, str(task.id))
        if model is None:
            return
        model.title = task.title
        model.description = task.description
        model.priority = task.priority.value
        model.status = task.status.value
        model.updated_at = task.updated_at
        self.session.flush()

    def delete(self, task_id: UUID) -> None:
        model = self.session.get(TaskModel, str(task_id))
        if model is not None:
            self.session.delete(model)
            self.session.flush()

    def _filters(
        self,
        list_id: UUID,
        status: TaskStatus | None,
        priority: Priority | None,
    ) -> list:
        clauses = [TaskModel.list_id == str(list_id)]
        if status is not None:
            clauses.append(TaskModel.status == status.value)
        if priority is not None:
            clauses.append(TaskModel.priority == priority.value)
        return clauses

    def list_by_list(
        self,
        list_id: UUID,
        limit: int,
        offset: int,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> list[Task]:
        stmt = (
            select(TaskModel)
            .where(*self._filters(list_id, status, priority))
            .order_by(TaskModel.created_at)
            .limit(limit)
            .offset(offset)
        )
        models = self.session.scalars(stmt).all()
        return [_to_domain(model) for model in models]

    def count_by_list(
        self,
        list_id: UUID,
        status: TaskStatus | None = None,
        priority: Priority | None = None,
    ) -> int:
        stmt = (
            select(func.count())
            .select_from(TaskModel)
            .where(*self._filters(list_id, status, priority))
        )
        return self.session.scalar(stmt) or 0

    def completion_counts(self, list_id: UUID) -> tuple[int, int]:
        """Una sola consulta de agregación (C8): no carga las tareas
        en memoria para contar."""
        completed_case = case(
            (TaskModel.status == TaskStatus.COMPLETED.value, 1), else_=0
        )
        stmt = select(
            func.coalesce(func.sum(completed_case), 0),
            func.count(),
        ).where(TaskModel.list_id == str(list_id))
        completed, total = self.session.execute(stmt).one()
        return int(completed), int(total)
