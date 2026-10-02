"""Caso de uso ChangeTaskStatus (B2, C3): cambia el estado y persiste;
permite volver de COMPLETED a PENDING; pedir el mismo estado no toca
updated_at en lo persistido; tarea de otra lista lanza
TaskNotFoundError y no cambia su estado."""

from datetime import datetime, timezone

import pytest

from app.application.change_task_status import ChangeTaskStatus
from app.domain import clock
from app.domain.enums import TaskStatus
from app.domain.exceptions import TaskNotFoundError
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


def test_changes_status_and_reads_back_from_repo() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task()
    use_case = ChangeTaskStatus(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(
        list_id=task_list.id, task_id=task.id, status=TaskStatus.COMPLETED
    )

    assert result.status == TaskStatus.COMPLETED
    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.status == TaskStatus.COMPLETED


def test_allows_completed_to_pending() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        status=TaskStatus.COMPLETED
    )
    use_case = ChangeTaskStatus(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    result = use_case.execute(
        list_id=task_list.id, task_id=task.id, status=TaskStatus.PENDING
    )

    assert result.status == TaskStatus.PENDING
    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.status == TaskStatus.PENDING


def test_same_status_does_not_change_updated_at_in_repo(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    creation_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    monkeypatch.setattr(clock, "utcnow", lambda: creation_time)
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        status=TaskStatus.PENDING
    )

    monkeypatch.setattr(
        clock, "utcnow", lambda: datetime(2026, 1, 2, tzinfo=timezone.utc)
    )
    use_case = ChangeTaskStatus(
        task_list_repository=task_list_repository, task_repository=task_repository
    )
    use_case.execute(list_id=task_list.id, task_id=task.id, status=TaskStatus.PENDING)

    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.status == TaskStatus.PENDING
    assert reread.updated_at == creation_time


def test_raises_not_found_for_task_in_another_list_and_status_unchanged() -> None:
    task_list_repository, task_repository, task_list, task = _repositories_with_task(
        status=TaskStatus.PENDING
    )
    other_list = TaskList(name="Otra lista")
    task_list_repository.add(other_list)
    use_case = ChangeTaskStatus(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(TaskNotFoundError):
        use_case.execute(
            list_id=other_list.id, task_id=task.id, status=TaskStatus.COMPLETED
        )

    reread = task_repository.get(task.id)
    assert reread is not None
    assert reread.status == TaskStatus.PENDING
