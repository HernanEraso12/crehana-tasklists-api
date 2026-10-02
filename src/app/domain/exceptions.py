"""Excepciones del dominio. No conocen HTTP; el mapeo a códigos vive en
`infrastructure/api/error_handlers.py`."""


class InvalidTaskListError(Exception):
    """Se lanza cuando una TaskList no cumple sus reglas de validación (B5)."""
