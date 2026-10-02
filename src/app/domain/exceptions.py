"""Excepciones del dominio. No conocen HTTP; el mapeo a códigos vive en
`infrastructure/api/error_handlers.py`."""

from uuid import UUID


class InvalidTaskListError(Exception):
    """Se lanza cuando una TaskList no cumple sus reglas de validación (B5)."""


class InvalidTaskError(Exception):
    """Se lanza cuando una Task no cumple sus reglas de validación (B6)."""


class InvalidCompletionCountsError(Exception):
    """Se lanza cuando los conteos para calcular la completitud (C8) son
    inválidos: negativos, o `completed` mayor que `total`."""


class TaskListNotFoundError(Exception):
    """Se lanza cuando no existe una TaskList con el id dado."""

    def __init__(self, list_id: UUID) -> None:
        self.list_id = list_id
        super().__init__(f"Task list {list_id} not found")


class TaskNotFoundError(Exception):
    """Se lanza cuando no existe una Task con el id dado, o cuando
    existe pero en otra lista (B9: no se revela que existe en otra)."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task {task_id} not found")
