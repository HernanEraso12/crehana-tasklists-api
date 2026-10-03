"""configure_logging: sin ella, los logger.info de `app` (p. ej.
LoggingNotifier) no llegan a ningún handler y no se ven en stdout.
Fija el nivel y el formato del logger `app`, sin tocar el logger raíz
ni la configuración de logging de uvicorn."""

import logging

import pytest

from app.infrastructure.logging_config import configure_logging

pytestmark = pytest.mark.unit


@pytest.fixture(autouse=True)
def _reset_app_logger() -> None:
    logger = logging.getLogger("app")
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)
    yield
    logger.handlers.clear()
    logger.setLevel(logging.NOTSET)


def test_sets_the_requested_level_on_the_app_logger() -> None:
    configure_logging("DEBUG")

    assert logging.getLogger("app").level == logging.DEBUG


def test_defaults_to_info_level() -> None:
    configure_logging()

    assert logging.getLogger("app").level == logging.INFO


def test_attaches_a_single_handler_with_timestamp_level_name_and_message() -> None:
    configure_logging("INFO")

    logger = logging.getLogger("app")
    assert len(logger.handlers) == 1
    formatter = logger.handlers[0].formatter
    assert formatter is not None
    assert formatter._fmt == "%(asctime)s %(levelname)s %(name)s: %(message)s"


def test_calling_twice_does_not_duplicate_handlers() -> None:
    configure_logging("INFO")
    configure_logging("INFO")

    assert len(logging.getLogger("app").handlers) == 1
