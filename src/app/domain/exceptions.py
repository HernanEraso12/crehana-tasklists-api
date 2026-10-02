"""Excepciones del dominio. No conocen HTTP; el mapeo a códigos vive en
`infrastructure/api/error_handlers.py`."""


class InvalidTaskListError(Exception):
    """Se lanza cuando una TaskList no cumple sus reglas de validación (B5)."""


class InvalidTaskError(Exception):
    """Se lanza cuando una Task no cumple sus reglas de validación (B6)."""


class InvalidCompletionCountsError(Exception):
    """Se lanza cuando los conteos para calcular la completitud (C8) son
    inválidos: negativos, o `completed` mayor que `total`."""
