"""Caso de uso DeleteTaskList: elimina una lista existente; lanza
TaskListNotFoundError si no existe; no afecta a otras listas."""

from uuid import uuid4

import pytest

from app.application.delete_task_list import DeleteTaskList
from app.domain.exceptions import TaskListNotFoundError
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def test_deletes_existing_list_and_subsequent_get_returns_none() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12")
    repository.add(existing)
    use_case = DeleteTaskList(repository=repository)

    use_case.execute(list_id=existing.id)

    assert repository.get(existing.id) is None


def test_raises_not_found_for_missing_list() -> None:
    repository = InMemoryTaskListRepository()
    use_case = DeleteTaskList(repository=repository)
    missing_id = uuid4()

    with pytest.raises(TaskListNotFoundError) as exc_info:
        use_case.execute(list_id=missing_id)

    assert exc_info.value.list_id == missing_id


def test_deleting_one_list_does_not_affect_others() -> None:
    repository = InMemoryTaskListRepository()
    keep = TaskList(name="Keep")
    remove = TaskList(name="Remove")
    repository.add(keep)
    repository.add(remove)
    use_case = DeleteTaskList(repository=repository)

    use_case.execute(list_id=remove.id)

    assert repository.get(remove.id) is None
    kept = repository.get(keep.id)
    assert kept is not None
    assert kept.name == "Keep"
