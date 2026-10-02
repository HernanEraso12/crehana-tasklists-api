"""Entidad de dominio Task (B1, B3, B6)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain import clock
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import InvalidTaskError

MAX_TITLE_LENGTH = 200


@dataclass
class Task:
    title: str
    list_id: UUID
    description: str | None = None
    priority: Priority = Priority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: clock.utcnow())
    updated_at: datetime = field(default_factory=lambda: clock.utcnow())

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise InvalidTaskError("El título de la tarea es obligatorio.")
        if len(self.title) > MAX_TITLE_LENGTH:
            raise InvalidTaskError(
                f"El título de la tarea no puede superar los "
                f"{MAX_TITLE_LENGTH} caracteres."
            )
