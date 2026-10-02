"""Entidad de dominio TaskList (B5)."""

from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4

from app.domain import clock
from app.domain.exceptions import InvalidTaskListError
from app.domain.sentinels import UNSET, _Unset

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

    def update(
        self,
        name: str | _Unset = UNSET,
        description: str | None | _Unset = UNSET,
    ) -> None:
        """Actualización parcial (C2). `UNSET` significa "no enviado":
        se conserva el valor actual. Valida el nombre igual que al
        crear. Solo toca `updated_at` si algo cambió de verdad."""
        changed = False

        if name is not UNSET:
            new_name = name.strip()
            if not new_name:
                raise InvalidTaskListError("El nombre de la lista es obligatorio.")
            if len(new_name) > MAX_NAME_LENGTH:
                raise InvalidTaskListError(
                    f"El nombre de la lista no puede superar los "
                    f"{MAX_NAME_LENGTH} caracteres."
                )
            if new_name != self.name:
                self.name = new_name
                changed = True

        if description is not UNSET and description != self.description:
            self.description = description
            changed = True

        if changed:
            self.updated_at = clock.utcnow()
