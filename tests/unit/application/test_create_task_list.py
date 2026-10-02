"""Caso de uso CreateTaskList: crea y persiste la lista en el repositorio;
propaga InvalidTaskListError si el nombre es inválido, sin guardar nada."""

import pytest

from app.application.create_task_list import CreateTaskList
from app.domain.exceptions import InvalidTaskListError
from tests.fakes import InMemoryTaskListRepository

pytestmark = pytest.mark.unit


def test_creates_and_persists_the_task_list() -> None:
    repository = InMemoryTaskListRepository()
    use_case = CreateTaskList(repository=repository)

    task_list = use_case.execute(name="Sprint 12", description="Opcional")

    assert task_list.name == "Sprint 12"
    assert task_list.description == "Opcional"
    assert repository.lists.get(task_list.id) is task_list


def test_propagates_invalid_name_without_saving_anything() -> None:
    repository = InMemoryTaskListRepository()
    use_case = CreateTaskList(repository=repository)

    with pytest.raises(InvalidTaskListError):
        use_case.execute(name="")

    assert repository.lists == {}
