"""Caso de uso: invitar por email a colaborar en una lista (E3)."""

from uuid import UUID

from app.application.common import get_task_list_or_raise
from app.domain.notifier import Notifier
from app.domain.repositories import TaskListRepository


class InviteToList:
    def __init__(self, repository: TaskListRepository, notifier: Notifier) -> None:
        self.repository = repository
        self.notifier = notifier

    def execute(self, list_id: UUID, email: str) -> None:
        get_task_list_or_raise(self.repository, list_id)
        self.notifier.notify_list_invitation(list_id, email)
