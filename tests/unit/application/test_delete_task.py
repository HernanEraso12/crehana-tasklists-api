"""Caso de uso DeleteTask: elimina la tarea; no afecta a otras de la
misma lista; tarea inexistente o de otra lista lanza TaskNotFoundError
sin eliminar nada."""

from uuid import uuid4

import pytest

from app.application.delete_task import DeleteTask
from app.domain.exceptions import TaskNotFoundError
from app.domain.task import Task
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository

pytestmark = pytest.mark.unit


def _repositories_with_task() -> (
    tuple[InMemoryTaskListRepository, InMemoryTaskRepository, TaskList, Task]
):
    task_list_repository = InMemoryTaskListRepository()
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    task_repository = InMemoryTaskRepository()
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)
    return task_list_repository, task_repository, task_list, task


def test_deletes_task_and_subsequent_get_returns_none() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task()
    use_case = DeleteTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    use_case.execute(list_id=task_list.id, task_id=task.id)

    assert task_repository.get(task.id) is None


def test_deleting_one_task_does_not_affect_others_in_the_same_list() -> None:
    task_list_repository, task_repository, task_list, keep = _repositories_with_task()
    remove = Task(title="Eliminar", list_id=task_list.id)
    task_repository.add(remove)
    use_case = DeleteTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    use_case.execute(list_id=task_list.id, task_id=remove.id)

    assert task_repository.get(remove.id) is None
    kept = task_repository.get(keep.id)
    assert kept is not None
    assert kept.title == "Escribir tests"


def test_raises_not_found_for_missing_task() -> None:
    task_list_repository, task_repository, task_list, _task = _repositories_with_task()
    use_case = DeleteTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )
    missing_task_id = uuid4()

    with pytest.raises(TaskNotFoundError) as exc_info:
        use_case.execute(list_id=task_list.id, task_id=missing_task_id)

    assert exc_info.value.task_id == missing_task_id


def test_raises_not_found_for_task_in_another_list_and_does_not_delete_it() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task()
    other_list = TaskList(name="Otra lista")
    task_list_repository.add(other_list)
    use_case = DeleteTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(TaskNotFoundError):
        use_case.execute(list_id=other_list.id, task_id=task.id)

    survivor = task_repository.get(task.id)
    assert survivor is not None
    assert survivor.title == "Escribir tests"
