"""Caso de uso UpdateTaskList: actualización parcial (C2) usando el
sentinel UNSET; propaga InvalidTaskListError sin cambiar nada y
TaskListNotFoundError si la lista no existe."""

from uuid import uuid4

import pytest

from app.application.update_task_list import UpdateTaskList
from app.domain.exceptions import InvalidTaskListError, TaskListNotFoundError
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def test_updates_name_and_keeps_description() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12", description="Original")
    repository.add(existing)
    use_case = UpdateTaskList(repository=repository)

    result = use_case.execute(list_id=existing.id, name="Sprint 13")

    assert result.name == "Sprint 13"
    assert result.description == "Original"
    assert repository.lists[existing.id].name == "Sprint 13"


def test_clears_description_with_none() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12", description="Original")
    repository.add(existing)
    use_case = UpdateTaskList(repository=repository)

    result = use_case.execute(list_id=existing.id, description=None)

    assert result.description is None
    assert repository.lists[existing.id].description is None


def test_invalid_name_raises_without_changing_anything() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12", description="Original")
    repository.add(existing)
    use_case = UpdateTaskList(repository=repository)

    with pytest.raises(InvalidTaskListError):
        use_case.execute(list_id=existing.id, name="   ")

    assert repository.lists[existing.id].name == "Sprint 12"
    assert repository.lists[existing.id].description == "Original"


def test_change_is_persisted_and_readable_via_get() -> None:
    """El repo fake guarda copias (fakes.py): si el caso de uso no llama
    a repository.update, mutar el objeto que devolvió get() no se nota
    aquí, porque esta lectura es independiente."""
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12", description="Original")
    repository.add(existing)
    use_case = UpdateTaskList(repository=repository)

    use_case.execute(list_id=existing.id, name="Sprint 13")

    reloaded = repository.get(existing.id)
    assert reloaded is not None
    assert reloaded.name == "Sprint 13"
    assert reloaded.description == "Original"


def test_raises_not_found_for_missing_list() -> None:
    repository = InMemoryTaskListRepository()
    use_case = UpdateTaskList(repository=repository)
    missing_id = uuid4()

    with pytest.raises(TaskListNotFoundError) as exc_info:
        use_case.execute(list_id=missing_id, name="Sprint 13")

    assert exc_info.value.list_id == missing_id
