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
    # UNSET (no datetime real) como default: __post_init__ lo detecta
    # y copia created_at, para no llamar al reloj dos veces y que
    # ambos campos salgan idénticos al crear.
    updated_at: datetime | _Unset = field(default=UNSET)

    def __post_init__(self) -> None:
        self.title = self._validated_title(self.title)
        if self.updated_at is UNSET:
            self.updated_at = self.created_at

    @staticmethod
    def _validated_title(title: str) -> str:
        """Recorta y valida un título de tarea (B6). Lo usan tanto la
        creación como `update`, para que ambas exijan lo mismo."""
        stripped = title.strip()
        if not stripped:
            raise InvalidTaskError("El título de la tarea es obligatorio.")
        if len(stripped) > MAX_TITLE_LENGTH:
            raise InvalidTaskError(
                f"El título de la tarea no puede superar los "
                f"{MAX_TITLE_LENGTH} caracteres."
            )
        return stripped

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
        """Actualización parcial (C2). No acepta `status`: solo
        `change_status` lo cambia (C3). `UNSET` significa "no enviado":
        se conserva el valor actual. Valida el título igual que al
        crear. Solo toca `updated_at` si algo cambió de verdad."""
        changed = False

        if title is not UNSET:
            new_title = self._validated_title(title)
            if new_title != self.title:
                self.title = new_title
                changed = True

        if description is not UNSET and description != self.description:
            self.description = description
            changed = True

        if priority is not UNSET and priority != self.priority:
            self.priority = priority
            changed = True

        if changed:
            self.updated_at = clock.utcnow()
