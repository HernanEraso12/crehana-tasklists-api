"""Caso de uso CreateTask: crea la tarea asociada a la lista y queda
guardada en el repositorio de tareas; propaga TaskListNotFoundError si
la lista no existe e InvalidTaskError si el título es inválido, sin
guardar nada en ninguno de los dos casos. El estado no es un
parámetro: toda tarea nace PENDING."""

from uuid import uuid4

import pytest

from app.application.create_task import CreateTask
from app.domain.enums import Priority, TaskStatus
from app.domain.exceptions import InvalidTaskError, TaskListNotFoundError
from app.domain.task_list import TaskList
from tests.fakes import InMemoryTaskListRepository, InMemoryTaskRepository

pytestmark = pytest.mark.unit


def test_creates_and_persists_the_task() -> None:
    task_list_repository = InMemoryTaskListRepository()
    existing_list = TaskList(name="Sprint 12")
    task_list_repository.add(existing_list)
    task_repository = InMemoryTaskRepository()
    use_case = CreateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    task = use_case.execute(
        list_id=existing_list.id,
        title="Escribir tests",
        description="Opcional",
        priority=Priority.HIGH,
    )

    assert task.list_id == existing_list.id
    assert task.title == "Escribir tests"
    assert task.description == "Opcional"
    assert task.priority == Priority.HIGH
    assert task.status == TaskStatus.PENDING
    stored = task_repository.tasks.get(task.id)
    assert stored is not None
    assert stored.title == "Escribir tests"


def test_defaults_to_pending_status_and_medium_priority() -> None:
    task_list_repository = InMemoryTaskListRepository()
    existing_list = TaskList(name="Sprint 12")
    task_list_repository.add(existing_list)
    task_repository = InMemoryTaskRepository()
    use_case = CreateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    task = use_case.execute(list_id=existing_list.id, title="Escribir tests")

    assert task.status == TaskStatus.PENDING
    assert task.priority == Priority.MEDIUM


def test_raises_task_list_not_found_without_saving_anything() -> None:
    task_list_repository = InMemoryTaskListRepository()
    task_repository = InMemoryTaskRepository()
    use_case = CreateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )
    missing_id = uuid4()

    with pytest.raises(TaskListNotFoundError):
        use_case.execute(list_id=missing_id, title="Escribir tests")

    assert task_repository.tasks == {}


def test_raises_invalid_title_without_saving_anything() -> None:
    task_list_repository = InMemoryTaskListRepository()
    existing_list = TaskList(name="Sprint 12")
    task_list_repository.add(existing_list)
    task_repository = InMemoryTaskRepository()
    use_case = CreateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )

    with pytest.raises(InvalidTaskError):
        use_case.execute(list_id=existing_list.id, title="   ")

    assert task_repository.tasks == {}
