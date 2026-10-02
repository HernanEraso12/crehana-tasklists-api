"""Caso de uso GetTaskList: devuelve la lista existente; lanza
TaskListNotFoundError con el list_id cuando no existe."""

from uuid import uuid4

import pytest

from app.application.get_task_list import GetTaskList
from app.domain.exceptions import TaskListNotFoundError
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def test_returns_the_existing_task_list() -> None:
    repository = InMemoryTaskListRepository()
    existing = TaskList(name="Sprint 12")
    repository.add(existing)
    use_case = GetTaskList(repository=repository)

    result = use_case.execute(list_id=existing.id)

    assert result is existing


def test_raises_not_found_with_the_id_when_missing() -> None:
    repository = InMemoryTaskListRepository()
    use_case = GetTaskList(repository=repository)
    missing_id = uuid4()

    with pytest.raises(TaskListNotFoundError) as exc_info:
        use_case.execute(list_id=missing_id)

    assert exc_info.value.list_id == missing_id
    assert str(missing_id) in str(exc_info.value)
