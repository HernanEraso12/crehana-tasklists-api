"""Puerto Notifier (A2, E2): el dominio declara el contrato de
notificación; la implementación (ficticia, E2) vive en `infrastructure`."""

from typing import Protocol
from uuid import UUID


class Notifier(Protocol):
    def notify_list_invitation(self, list_id: UUID, email: str) -> None: ...
