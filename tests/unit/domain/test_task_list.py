"""Validación del nombre de TaskList (B5): obligatorio, 1-100 caracteres,
se recorta espacios al inicio o al final, no vacío tras recortar."""

import pytest

from app.domain.exceptions import InvalidTaskListError
from app.domain.task_list import TaskList

pytestmark = pytest.mark.unit


def test_creates_task_list_with_valid_name() -> None:
    task_list = TaskList(name="Sprint 12")

    assert task_list.name == "Sprint 12"


def test_rejects_empty_name() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="")


def test_rejects_whitespace_only_name() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="   ")


def test_strips_leading_and_trailing_spaces() -> None:
    task_list = TaskList(name=" Sprint ")

    assert task_list.name == "Sprint"


def test_rejects_name_longer_than_100_characters() -> None:
    with pytest.raises(InvalidTaskListError):
        TaskList(name="a" * 101)


def test_accepts_name_of_exactly_100_characters() -> None:
    task_list = TaskList(name="a" * 100)

    assert len(task_list.name) == 100
