"""Caso de uso GetTask (B9): devuelve la tarea de la lista correcta;
tarea inexistente o que existe en otra lista lanza TaskNotFoundError;
lista inexistente lanza TaskListNotFoundError."""

from uuid import uuid4

import pytest

from app.application.get_task import GetTask
from app.domain.exceptions import TaskListNotFoundError, TaskNotFoundError
from app.domain.task import Task
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository

pytestmark = pytest.mark.unit


def _repositories_with_list() -> (
    tuple[InMemoryTaskListRepository, InMemoryTaskRepository, TaskList]
):
    task_list_repository = InMemoryTaskListRepository()
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    return task_list_repository, InMemoryTaskRepository(), task_list


def test_returns_the_task_from_the_correct_list() -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)
    use_case = GetTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(list_id=task_list.id, task_id=task.id)

    assert result.id == task.id
    assert result.title == "Escribir tests"


def test_raises_not_found_for_missing_task() -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    use_case = GetTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )
    missing_task_id = uuid4()

    with pytest.raises(TaskNotFoundError) as exc_info:
        use_case.execute(list_id=task_list.id, task_id=missing_task_id)

    assert exc_info.value.task_id == missing_task_id


def test_raises_not_found_for_task_belonging_to_another_list() -> None:
    task_list_repository, task_repository, task_list = _repositories_with_list()
    other_list = TaskList(name="Otra lista")
    task_list_repository.add(other_list)
    task_in_other_list = Task(title="De otra lista", list_id=other_list.id)
    task_repository.add(task_in_other_list)
    use_case = GetTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(TaskNotFoundError) as exc_info:
        use_case.execute(list_id=task_list.id, task_id=task_in_other_list.id)

    assert exc_info.value.task_id == task_in_other_list.id


def test_raises_task_list_not_found_for_missing_list() -> None:
    task_list_repository = InMemoryTaskListRepository()
    task_repository = InMemoryTaskRepository()
    use_case = GetTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )
    missing_list_id = uuid4()

    with pytest.raises(TaskListNotFoundError):
        use_case.execute(list_id=missing_list_id, task_id=uuid4())
