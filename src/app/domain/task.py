"""Entidad de dominio Task (B1, B2, B3, B6)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain import clock
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import InvalidTaskError
from app.domain.sentinels import UNSET, _Unset

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

    def change_status(self, new_status: TaskStatus) -> None:
        """Cambia el estado (B2). Cualquier transición está permitida.
        Si el nuevo estado es el mismo, es idempotente y no toca
        `updated_at` (no hay un cambio real que registrar)."""
        if new_status == self.status:
            return
        self.status = new_status
        self.updated_at = clock.utcnow()

    def update(
        self,
        title: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
        priority: Priority | _Unset = UNSET,
    ) -> None:
        """Stub temporal: no hace nada todavía (rojo pendiente de GREEN)."""
