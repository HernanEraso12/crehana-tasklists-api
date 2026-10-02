"""Caso de uso UpdateTask (C2, C3): actualización parcial sin tocar el
estado; propaga InvalidTaskError sin cambiar nada y TaskNotFoundError
si la tarea no existe o es de otra lista."""

import pytest

from app.application.update_task import UpdateTask
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import InvalidTaskError, TaskNotFoundError
from app.domain.task import Task
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository

pytestmark = pytest.mark.unit


def _repositories_with_task(
    **task_kwargs,
) -> tuple[InMemoryTaskListRepository, InMemoryTaskRepository, TaskList, Task]:
    task_list_repository = InMemoryTaskListRepository()
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    task_repository = InMemoryTaskRepository()
    task = Task(title="Escribir tests", list_id=task_list.id, **task_kwargs)
    task_repository.add(task)
    return task_list_repository, task_repository, task_list, task


def test_updates_title_and_keeps_description_priority_and_status() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        description="Original", priority=Priority.LOW, status=TaskStatus.IN_PROGRESS
    )
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(
        list_id=task_list.id, task_id=task.id, title="Escribir tests v2"
    )

    assert result.title == "Escribir tests v2"
    assert result.description == "Original"
    assert result.priority == Priority.LOW
    assert result.status == TaskStatus.IN_PROGRESS


def test_updates_priority() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        priority=Priority.LOW
    )
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(
        list_id=task_list.id, task_id=task.id, priority=Priority.HIGH
    )

    assert result.priority == Priority.HIGH


def test_clears_description_with_none() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        description="Original"
    )
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(list_id=task_list.id, task_id=task.id, description=None)

    assert result.description is None


def test_invalid_title_raises_and_reread_task_is_unchanged() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        description="Original"
    )
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(InvalidTaskError):
        use_case.execute(list_id=task_list.id, task_id=task.id, title="   ")

    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.title == "Escribir tests"
    assert reread.description == "Original"


def test_change_is_persisted_and_readable_via_get() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task()
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    use_case.execute(list_id=task_list.id, task_id=task.id, title="Escribir tests v2")

    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.title == "Escribir tests v2"


def test_raises_not_found_for_task_belonging_to_another_list() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task()
    other_list = TaskList(name="Otra lista")
    task_list_repository.add(other_list)
    use_case = UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(TaskNotFoundError):
        use_case.execute(
            list_id=other_list.id, task_id=task.id, title="Escribir tests v2"
        )
