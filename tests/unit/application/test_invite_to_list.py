"""Caso de uso InviteToList: notifica la invitación cuando la lista
existe; lanza TaskListNotFoundError sin notificar si no existe (E3)."""

from uuid import uuid4

import pytest

from app.application.invite_to_list import InviteToList
from app.domain.exceptions import TaskListNotFoundError
from app.domain.task_list import TaskList
from tests.fakes import InMemoryNotifier, InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def test_notifies_invitation_for_existing_list() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12")
    repository.add(existing)
    notifier = InMemoryNotifier()
    use_case = InviteToList(repository=repository, notifier=notifier)

    use_case.execute(list_id=existing.id, email="colega@example.com")

    assert notifier.invitations == [(existing.id, "colega@example.com")]


def test_raises_not_found_and_does_not_notify_for_missing_list() -> None:
    repository = InMemoryTaskListRepository()
    notifier = InMemoryNotifier()
    use_case = InviteToList(repository=repository, notifier=notifier)
    missing_id = uuid4()

    with pytest.raises(TaskListNotFoundError) as exc_info:
        use_case.execute(list_id=missing_id, email="colega@example.com")

    assert exc_info.value.list_id == missing_id
    assert notifier.invitations == []
