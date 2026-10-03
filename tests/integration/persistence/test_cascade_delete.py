"""Borrado en cascada lista -> tareas (B8). Es una regla de la base de
datos (ON DELETE CASCADE en la FK, con PRAGMA foreign_keys=ON ya
activo), no algo que decida el repositorio en Python. Por eso corre
solo contra SQLAlchemy, aparte de la suite de contrato."""

import pytest

from app.domain.task import Task
from app.domain.task_list import TaskList
from tests.integration.persistence.sqlite_support import (
    create_sqlalchemy_repositories,
    dispose_sqlalchemy_repositories,
)

pytestmark = pytest.mark.integration


@pytest.fixture
def repositories():
    task_list_repository, task_repository = create_sqlalchemy_repositories()
    yield task_list_repository, task_repository
    dispose_sqlalchemy_repositories(task_list_repository)


def test_deleting_a_list_cascades_to_its_tasks(repositories) -> None:
    task_list_repository, task_repository = repositories
    task_list = TaskList(name="Sprint 12")
    task_list_repository.add(task_list)
    task = Task(title="Escribir tests", list_id=task_list.id)
    task_repository.add(task)

    task_list_repository.delete(task_list.id)

    assert task_repository.get(task.id) is None
    assert task_repository.count_by_list(task_list.id) == 0


def test_deleting_a_list_does_not_affect_tasks_of_other_lists(repositories) -> None:
    task_list_repository, task_repository = repositories
    list_a = TaskList(name="Lista A")
    list_b = TaskList(name="Lista B")
    task_list_repository.add(list_a)
    task_list_repository.add(list_b)
    removed = Task(title="Se borra con A", list_id=list_a.id)
    survivor = Task(title="Sobrevive en B", list_id=list_b.id)
    task_repository.add(removed)
    task_repository.add(survivor)

    task_list_repository.delete(list_a.id)

    assert task_repository.get(removed.id) is None
    assert task_repository.count_by_list(list_a.id) == 0
    found = task_repository.get(survivor.id)
    assert found is not None
    assert found.title == "Sobrevive en B"
    assert task_repository.count_by_list(list_b.id) == 1
