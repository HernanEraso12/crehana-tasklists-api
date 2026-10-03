"""LoggingNotifier (E2): el bonus es ficticio, pero la invitación debe
quedar registrada en el log con el email y la lista, con severidad
INFO (visible con el nivel por defecto de `configure_logging`)."""

import logging
from uuid import uuid4

import pytest

from app.infrastructure.notifications import LoggingNotifier

pytestmark = pytest.mark.unit


def test_notify_list_invitation_logs_an_info_record_with_list_id_and_email(
    caplog: pytest.LogCaptureFixture,
) -> None:
    notifier = LoggingNotifier()
    list_id = uuid4()
    email = "colega@example.com"

    with caplog.at_level(logging.INFO, logger="app.notifications"):
        notifier.notify_list_invitation(list_id, email)

    assert len(caplog.records) == 1
    record = caplog.records[0]
    assert record.levelno == logging.INFO
    assert str(list_id) in record.getMessage()
    assert email in record.getMessage()
