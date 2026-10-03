"""Composition root de la API: cablea repositorios y casos de uso con
`Depends`. Es el único lugar de `infrastructure` que conoce tanto
`infrastructure/persistence` como `application`.

La sesión es una por request: `commit` si todo sale bien, `rollback`
si hay una excepción, siempre se cierra (A5, D4)."""

from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.change_task_status import ChangeTaskStatus
from app.application.create_task import CreateTask
from app.application.create_task_list import CreateTaskList
from app.application.delete_task import DeleteTask
from app.application.delete_task_list import DeleteTaskList
from app.application.get_task import GetTask
from app.application.get_task_list import GetTaskList
from app.application.invite_to_list import InviteToList
from app.application.list_task_lists import ListTaskLists
from app.application.list_tasks import ListTasks
from app.application.update_task import UpdateTask
from app.application.update_task_list import UpdateTaskList
from app.domain.notifier import Notifier
from app.domain.repositories import TaskListRepository, TaskRepository
from app.infrastructure.config import Settings
from app.infrastructure.notifications import LoggingNotifier
from app.infrastructure.persistence.database import (
    create_session_factory,
    create_sqlalchemy_engine,
)
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)

_settings = Settings()
_engine = create_sqlalchemy_engine(_settings.database_url)
_session_factory = create_session_factory(_engine)
_notifier = LoggingNotifier()


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


def get_task_repository(
    session: Session = Depends(get_db_session),
) -> TaskRepository:
    return SqlAlchemyTaskRepository(session)


def get_create_task_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> CreateTask:
    return CreateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_get_task_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> GetTask:
    return GetTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_update_task_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> UpdateTask:
    return UpdateTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_delete_task_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> DeleteTask:
    return DeleteTask(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_change_task_status_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> ChangeTaskStatus:
    return ChangeTaskStatus(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_list_tasks_use_case(
    task_list_repository: TaskListRepository = Depends(get_task_list_repository),
    task_repository: TaskRepository = Depends(get_task_repository),
) -> ListTasks:
    return ListTasks(
        task_list_repository=task_list_repository, task_repository=task_repository
    )


def get_notifier() -> Notifier:
    return _notifier


def get_invite_to_list_use_case(
    repository: TaskListRepository = Depends(get_task_list_repository),
    notifier: Notifier = Depends(get_notifier),
) -> InviteToList:
    return InviteToList(repository=repository, notifier=notifier)
