"""Entidad de dominio TaskList (B5)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain import clock
from app.domain.exceptions import InvalidTaskListError

MAX_NAME_LENGTH = 100


@dataclass
class TaskList:
    name: str
    description: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: clock.utcnow())
    updated_at: datetime = field(default_factory=lambda: clock.utcnow())

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise InvalidTaskListError("El nombre de la lista es obligatorio.")
        if len(self.name) > MAX_NAME_LENGTH:
            raise InvalidTaskListError(
                f"El nombre de la lista no puede superar los "
                f"{MAX_NAME_LENGTH} caracteres."
            )
