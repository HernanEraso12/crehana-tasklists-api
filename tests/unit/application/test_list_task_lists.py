"""Caso de uso ListTaskLists: paginación (C5) y orden por created_at
ascendente (C6). El orden se controla con monkeypatch sobre
app.domain.clock.utcnow, sin depender del reloj real."""

from datetime import datetime, timezone

import pytest

from app.application.list_task_lists import ListTaskLists
from app.domain import clock
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def _task_list_created_at(
    monkeypatch: pytest.MonkeyPatch, name: str, created_at: datetime
) -> TaskList:
    monkeypatch.setattr(clock, "utcnow", lambda: created_at)
    return TaskList(name=name)


def test_empty_repository_returns_an_empty_page() -> None:
    repository = InMemoryTaskListRepository()
    use_case = ListTaskLists(repository=repository)

    page = use_case.execute(limit=20, offset=0)

    assert page.items == []
    assert page.total == 0
    assert page.limit == 20
    assert page.offset == 0


def test_returns_first_page_ordered_by_created_at(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    repository = InMemoryTaskListRepository()
    # created_at se asigna vía monkeypatch, no por orden de inserción:
    # se crean y agregan C, A, B (desordenadas) para que el test solo
    # pase si el caso de uso ordena por created_at.
    third = _task_list_created_at(
        monkeypatch, "C", datetime(2026, 1, 3, tzinfo=timezone.utc)
    )
    first = _task_list_created_at(
        monkeypatch, "A", datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    second = _task_list_created_at(
        monkeypatch, "B", datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    for task_list in (third, first, second):
        repository.add(task_list)
    use_case = ListTaskLists(repository=repository)

    page = use_case.execute(limit=2, offset=0)

    assert [item.name for item in page.items] == ["A", "B"]
    assert page.total == 3
    assert page.limit == 2
    assert page.offset == 0


def test_returns_second_page_with_offset(monkeypatch: pytest.MonkeyPatch) -> None:
    repository = InMemoryTaskListRepository()
    third = _task_list_created_at(
        monkeypatch, "C", datetime(2026, 1, 3, tzinfo=timezone.utc)
    )
    first = _task_list_created_at(
        monkeypatch, "A", datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    second = _task_list_created_at(
        monkeypatch, "B", datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    for task_list in (third, first, second):
        repository.add(task_list)
    use_case = ListTaskLists(repository=repository)

    page = use_case.execute(limit=2, offset=2)

    assert [item.name for item in page.items] == ["C"]
    assert page.total == 3
