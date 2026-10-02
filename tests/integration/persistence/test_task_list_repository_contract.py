"""Suite de contrato de TaskListRepository (D2): la misma batería corre
contra el fake en memoria y contra SqlAlchemyTaskListRepository sobre
SQLite en memoria, para demostrar que ambos cumplen el mismo contrato
(LSP). SQLite: StaticPool (una sola conexión compartida) y
PRAGMA foreign_keys=ON por conexión (A9)."""

from datetime import datetime, timezone
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.domain import clock
from app.domain.task_list import TaskList
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)
from tests.fakes import InMemoryTaskListRepository
from tests.integration.persistence.sqlite_support import create_in_memory_sqlite_engine

pytestmark = pytest.mark.integration


def _make_sqlalchemy_repository() -> SqlAlchemyTaskListRepository:
    engine = create_in_memory_sqlite_engine()
    Base.metadata.create_all(engine)
    session = Session(engine)
    return SqlAlchemyTaskListRepository(session)


@pytest.fixture(params=["fake", "sqlalchemy"])
def repository(request: pytest.FixtureRequest):
    if request.param == "fake":
        return InMemoryTaskListRepository()
    return _make_sqlalchemy_repository()


def test_add_and_get_return_an_equal_task_list(repository) -> None:
    task_list = TaskList(name="Sprint 12", description="Opcional")

    repository.add(task_list)
    found = repository.get(task_list.id)

    assert found == task_list


def test_get_of_missing_id_returns_none(repository) -> None:
    assert repository.get(uuid4()) is None


def test_update_persists_changes(repository) -> None:
    task_list = TaskList(name="Sprint 12")
    repository.add(task_list)

    task_list.update(name="Sprint 13")
    repository.update(task_list)

    found = repository.get(task_list.id)
    assert found is not None
    assert found.name == "Sprint 13"


def test_delete_removes_the_task_list(repository) -> None:
    task_list = TaskList(name="Sprint 12")
    repository.add(task_list)
    # Confirma que existe antes de borrar: si no, "None después de
    # borrar" pasaría trivialmente incluso sin borrar nada.
    assert repository.get(task_list.id) is not None

    repository.delete(task_list.id)

    assert repository.get(task_list.id) is None


def test_list_orders_by_created_at_and_paginates(
    repository, monkeypatch: pytest.MonkeyPatch
) -> None:
    def _task_list_created_at(name: str, created_at: datetime) -> TaskList:
        monkeypatch.setattr(clock, "utcnow", lambda: created_at)
        return TaskList(name=name)

    # Se agregan desordenadas (C, A, B) a propósito: el orden debe
    # venir de created_at, no del orden de inserción.
    third = _task_list_created_at("C", datetime(2026, 1, 3, tzinfo=timezone.utc))
    first = _task_list_created_at("A", datetime(2026, 1, 1, tzinfo=timezone.utc))
    second = _task_list_created_at("B", datetime(2026, 1, 2, tzinfo=timezone.utc))
    for task_list in (third, first, second):
        repository.add(task_list)

    first_page = repository.list(limit=2, offset=0)
    second_page = repository.list(limit=2, offset=2)

    assert [tl.name for tl in first_page] == ["A", "B"]
    assert [tl.name for tl in second_page] == ["C"]


def test_count_counts_all_task_lists(repository) -> None:
    repository.add(TaskList(name="Sprint 12"))
    repository.add(TaskList(name="Sprint 13"))

    assert repository.count() == 2
