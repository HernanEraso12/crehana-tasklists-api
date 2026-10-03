"""Implementación ficticia del puerto Notifier (E2): solo registra la
invitación en el log, sin enviar nada de verdad."""

import logging
from uuid import UUID

logger = logging.getLogger("app.notifications")


class LoggingNotifier:
    def notify_list_invitation(self, list_id: UUID, email: str) -> None:
        logger.info("Invitation sent: list_id=%s email=%s", list_id, email)
