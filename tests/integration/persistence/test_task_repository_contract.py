"""Suite de contrato de TaskRepository (D2): la misma batería corre
contra el fake en memoria y contra SqlAlchemyTaskRepository sobre
SQLite en memoria, para demostrar que ambos cumplen el mismo contrato
(LSP). Como la tabla de tareas tiene clave foránea a listas, cada test
crea primero la lista padre con el repositorio de listas
correspondiente."""

from datetime import datetime, timezone
from uuid import UUID, uuid4

import pytest
from sqlalchemy.orm import Session

from app.domain import clock
from app.domain.enums import Priority, TaskStatus
from app.domain.task import Task
from app.domain.task_list import TaskList
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository
from tests.integration.persistence.sqlite_support import create_in_memory_sqlite_engine

pytestmark = pytest.mark.integration


def _make_fake_repositories() -> (
    tuple[InMemoryTaskListRepository, InMemoryTaskRepository]
):
    return InMemoryTaskListRepository(), InMemoryTaskRepository()


def _make_sqlalchemy_repositories() -> (
    tuple[SqlAlchemyTaskListRepository, SqlAlchemyTaskRepository]
):
    engine = create_in_memory_sqlite_engine()
    Base.metadata.create_all(engine)
    session = Session(engine)
    return SqlAlchemyTaskListRepository(session), SqlAlchemyTaskRepository(session)


@pytest.fixture(params=["fake", "sqlalchemy"])
def repositories(request: pytest.FixtureRequest):
    if request.param == "fake":
        return _make_fake_repositories()
    return _make_sqlalchemy_repositories()


def _new_list(task_list_repository, name: str = "Sprint 12") -> TaskList:
    task_list = TaskList(name=name)
    task_list_repository.add(task_list)
    return task_list


def _task_created_at(
    monkeypatch: pytest.MonkeyPatch,
    list_id: UUID,
    title: str,
    created_at: datetime,
    **kwargs,
) -> Task:
    monkeypatch.setattr(clock, "utcnow", lambda: created_at)
    return Task(title=title, list_id=list_id, **kwargs)


def test_add_and_get_return_an_equal_task(repositories) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    task = Task(
        title="Escribir tests",
        list_id=task_list.id,
        description="Opcional",
        priority=Priority.HIGH,
        status=TaskStatus.COMPLETED,
    )

    task_repository.add(task)
    found = task_repository.get(task.id)

    assert found == task


def test_get_of_missing_id_returns_none(repositories) -> None:
    _task_list_repository, task_repository = repositories

    assert task_repository.get(uuid4()) is None


def test_update_persists_changes(repositories) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)
    assert task_repository.get(task.id) is not None

    task.update(title="Escribir tests v2")
    task_repository.update(task)

    found = task_repository.get(task.id)
    assert found is not None
    assert found.title == "Escribir tests v2"


def test_delete_removes_the_task(repositories) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)
    assert task_repository.get(task.id) is not None

    task_repository.delete(task.id)

    assert task_repository.get(task.id) is None


def test_list_by_list_filters_by_status(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
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

    found = task_repository.list_by_list(
        task_list.id, limit=20, offset=0, status=TaskStatus.COMPLETED
    )

    assert [t.title for t in found] == ["Completed"]


def test_list_by_list_filters_by_priority(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
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

    found = task_repository.list_by_list(
        task_list.id, limit=20, offset=0, priority=Priority.HIGH
    )

    assert [t.title for t in found] == ["High"]


def test_list_by_list_combines_filters_with_and(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
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

    found = task_repository.list_by_list(
        task_list.id,
        limit=20,
        offset=0,
        status=TaskStatus.COMPLETED,
        priority=Priority.HIGH,
    )

    assert [t.title for t in found] == ["Match"]


def test_list_by_list_paginates_and_orders_by_created_at(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    # Se crean y agregan desordenadas (C, A, B) a propósito: el orden
    # debe venir de created_at (reloj controlado), no de la inserción.
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

    first_page = task_repository.list_by_list(task_list.id, limit=2, offset=0)
    second_page = task_repository.list_by_list(task_list.id, limit=2, offset=2)

    assert [t.title for t in first_page] == ["A", "B"]
    assert [t.title for t in second_page] == ["C"]


def test_list_by_list_excludes_tasks_from_other_lists(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository, "Sprint 12")
    other_list = _new_list(task_list_repository, "Otra lista")
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

    found = task_repository.list_by_list(task_list.id, limit=20, offset=0)

    assert [t.title for t in found] == ["Mine"]


def test_count_by_list_respects_filters(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    for i, priority in enumerate((Priority.LOW, Priority.HIGH, Priority.HIGH)):
        task = _task_created_at(
            monkeypatch,
            task_list.id,
            f"Task {i}",
            datetime(2026, 1, i + 1, tzinfo=timezone.utc),
            priority=priority,
        )
        task_repository.add(task)

    assert task_repository.count_by_list(task_list.id) == 3
    assert task_repository.count_by_list(task_list.id, priority=Priority.HIGH) == 2


def test_completion_counts_for_empty_list_is_zero_zero(repositories) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)

    assert task_repository.completion_counts(task_list.id) == (0, 0)


def test_completion_counts_reflects_completed_over_total(
    repositories, monkeypatch: pytest.MonkeyPatch
) -> None:
    task_list_repository, task_repository = repositories
    task_list = _new_list(task_list_repository)
    for i, status in enumerate(
        (TaskStatus.COMPLETED, TaskStatus.PENDING, TaskStatus.PENDING)
    ):
        task = _task_created_at(
            monkeypatch,
            task_list.id,
            f"Task {i}",
            datetime(2026, 1, i + 1, tzinfo=timezone.utc),
            status=status,
        )
        task_repository.add(task)

    assert task_repository.completion_counts(task_list.id) == (1, 3)
