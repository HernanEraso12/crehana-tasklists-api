"""Modelos ORM SQLAlchemy 2.0, estilo tipado (A5). No se exponen fuera
de `infrastructure/persistence`: los repositorios mapean explícitamente
entre estos modelos y las entidades de dominio (`app.domain.task_list`,
`app.domain.task`).

`id` como `String` (UUID como texto) y fechas con `DateTime(timezone=True)`
para portabilidad entre SQLite y PostgreSQL (A7, A8)."""

from datetime import datetime

from sqlalchemy import DateTime, String
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
