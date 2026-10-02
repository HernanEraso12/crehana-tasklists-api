"""Caso de uso ListTasks: filtros (C4, combinables con AND), paginación
(C5) y orden por created_at (C6). El porcentaje de completitud no es
parte de este caso de uso."""

from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.application.list_tasks import ListTasks
from app.domain import clock
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import TaskListNotFoundError
from app.domain.task import Task
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository

pytestmark = pytest.mark.unit


def _task_created_at(
    monkeypatch: pytest.MonkeyPatch,
    list_id: UUID,
    title: str,
    created_at: datetime,
    **kwargs,
) -> Task:
    monkeypatch.setattr(clock, "utcnow", lambda: created_at)
    return Task(title=title, list_id=list_id, **kwargs)


def _repositories_with_list() -> (
    tuple[InMemoryTaskListRepository, InMemoryTaskRepository, TaskList]
):
    task_list_repository = InMemoryTaskListRepository()
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    return task_list_repository, InMemoryTaskRepository(), task_list


def test_returns_all_tasks_of_the_list_without_filters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    a = _task_created_at(
        monkeypatch, task_list.id, "A", datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    b = _task_created_at(
        monkeypatch, task_list.id, "B", datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    task_repository.add(a)
    task_repository.add(b)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(list_id=task_list.id, limit=20, offset=0)

    assert [t.title for t in page.items] == ["A", "B"]
    assert page.total == 2
    assert page.limit == 20
    assert page.offset == 0


def test_filters_by_status(monkeypatch: pytest.MonkeyPatch) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    pending = _task_created_at(
        monkeypatch,
        task_list.id,
        "Pending",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        status=TaskStatus.PENDING,
    )
    completed = _task_created_at(
        monkeypatch,
        task_list.id,
        "Completed",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        status=TaskStatus.COMPLETED,
    )
    task_repository.add(pending)
    task_repository.add(completed)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(
        list_id=task_list.id, limit=20, offset=0, status=TaskStatus.COMPLETED
    )

    assert [t.title for t in page.items] == ["Completed"]
    assert page.total == 1


def test_filters_by_priority(monkeypatch: pytest.MonkeyPatch) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    low = _task_created_at(
        monkeypatch,
        task_list.id,
        "Low",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        priority=Priority.LOW,
    )
    high = _task_created_at(
        monkeypatch,
        task_list.id,
        "High",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        priority=Priority.HIGH,
    )
    task_repository.add(low)
    task_repository.add(high)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(
        list_id=task_list.id, limit=20, offset=0, priority=Priority.HIGH
    )

    assert [t.title for t in page.items] == ["High"]
    assert page.total == 1


def test_combines_status_and_priority_filters_with_and(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    match = _task_created_at(
        monkeypatch,
        task_list.id,
        "Match",
        datetime(2026, 1, 1, tzinfo=timezone.utc),
        status=TaskStatus.COMPLETED,
        priority=Priority.HIGH,
    )
    only_status = _task_created_at(
        monkeypatch,
        task_list.id,
        "OnlyStatus",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
        status=TaskStatus.COMPLETED,
        priority=Priority.LOW,
    )
    only_priority = _task_created_at(
        monkeypatch,
        task_list.id,
        "OnlyPriority",
        datetime(2026, 1, 3, tzinfo=timezone.utc),
        status=TaskStatus.PENDING,
        priority=Priority.HIGH,
    )
    for task in (match, only_status, only_priority):
        task_repository.add(task)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(
        list_id=task_list.id,
        limit=20,
        offset=0,
        status=TaskStatus.COMPLETED,
        priority=Priority.HIGH,
    )

    assert [t.title for t in page.items] == ["Match"]
    assert page.total == 1


def test_does_not_include_tasks_from_other_lists(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    other_list = TaskList(name="Otra lista")
    task_list_repository.add(other_list)
    mine = _task_created_at(
        monkeypatch, task_list.id, "Mine", datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    other = _task_created_at(
        monkeypatch,
        other_list.id,
        "Other",
        datetime(2026, 1, 2, tzinfo=timezone.utc),
    )
    task_repository.add(mine)
    task_repository.add(other)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(list_id=task_list.id, limit=20, offset=0)

    assert [t.title for t in page.items] == ["Mine"]
    assert page.total == 1


def test_paginates_with_limit_and_offset(monkeypatch: pytest.MonkeyPatch) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    for i, letter in enumerate(("A", "B", "C")):
        task = _task_created_at(
            monkeypatch,
            task_list.id,
            letter,
            datetime(2026, 1, i + 1, tzinfo=timezone.utc),
        )
        task_repository.add(task)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    first_page = use_case.execute(list_id=task_list.id, limit=2, offset=0)
    second_page = use_case.execute(list_id=task_list.id, limit=2, offset=2)

    assert [t.title for t in first_page.items] == ["A", "B"]
    assert first_page.total == 3
    assert [t.title for t in second_page.items] == ["C"]
    assert second_page.total == 3


def test_orders_by_created_at(monkeypatch: pytest.MonkeyPatch) -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    # Se crean y agregan desordenadas (C, A, B) a propósito: el orden
    # debe venir de created_at, no del orden de inserción.
    third = _task_created_at(
        monkeypatch, task_list.id, "C", datetime(2026, 1, 3, tzinfo=timezone.utc)
    )
    first = _task_created_at(
        monkeypatch, task_list.id, "A", datetime(2026, 1, 1, tzinfo=timezone.utc)
    )
    second = _task_created_at(
        monkeypatch, task_list.id, "B", datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    for task in (third, first, second):
        task_repository.add(task)
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    page = use_case.execute(list_id=task_list.id, limit=20, offset=0)

    assert [t.title for t in page.items] == ["A", "B", "C"]


def test_raises_task_list_not_found_for_missing_list() -> None:
    task_list_repository = InMemoryTaskListRepository()
    task_repository = InMemoryTaskRepository()
    use_case = ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(TaskListNotFoundError):
        use_case.execute(
            list_id=UUID("00000000-0000-0000-0000-000000000000"), limit=20, offset=0
        )
