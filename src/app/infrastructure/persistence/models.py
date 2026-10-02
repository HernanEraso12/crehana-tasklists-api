"""Modelos ORM SQLAlchemy 2.0, estilo tipado (A5). No se exponen fuera
de `infrastructure/persistence`: los repositorios mapean explícitamente
entre estos modelos y las entidades de dominio (`app.domain.task_list`,
`app.domain.task`).

`id` como `String` (UUID como texto) y fechas con `DateTime(timezone=True)`
para portabilidad entre SQLite y PostgreSQL (A7, A8)."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.persistence.database import Base


class TaskListModel(Base):
    __tablename__ = "task_lists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    # ondelete="CASCADE" (B8): borrar una lista borra sus tareas; es
    # la base de datos quien lo hace, no un borrado manual en Python.
    list_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("task_lists.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(1000))
    # Enums como String, no tipo nativo (A8): portabilidad SQLite/Postgres.
    priority: Mapped[str] = mapped_column(String(10), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False
    )
