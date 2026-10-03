"""Composition root de la API: cablea repositorios y casos de uso con
`Depends`. Es el único lugar de `infrastructure` que conoce tanto
`infrastructure/persistence` como `application`.

La sesión es una por request: `commit` si todo sale bien, `rollback`
si hay una excepción, siempre se cierra (A5, D4)."""

from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.create_task_list import CreateTaskList
from app.application.delete_task_list import DeleteTaskList
from app.application.get_task_list import GetTaskList
from app.application.list_task_lists import ListTaskLists
from app.application.update_task_list import UpdateTaskList
from app.domain.repositories import TaskListRepository
from app.infrastructure.config import Settings
from app.infrastructure.persistence.database import (
    create_session_factory,
    create_sqlalchemy_engine,
)
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)

_settings = Settings()
_engine = create_sqlalchemy_engine(_settings.database_url)
_session_factory = create_session_factory(_engine)


def get_db_session() -> Iterator[Session]:
    session = _session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_task_list_repository(
    session: Session = Depends(get_db_session),
) -> TaskListRepository:
    return SqlAlchemyTaskListRepository(session)


def get_create_task_list_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
) -> CreateTaskList:
    return CreateTaskList(repository=repository)


def get_get_task_list_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
) -> GetTaskList:
    return GetTaskList(repository=repository)


def get_list_task_lists_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
) -> ListTaskLists:
    return ListTaskLists(repository=repository)


def get_update_task_list_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
) -> UpdateTaskList:
    return UpdateTaskList(repository=repository)


def get_delete_task_list_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
) -> DeleteTaskList:
    return DeleteTaskList(repository=repository)
