"""SQLite en memoria para las suites de integración de persistencia
(A9): una sola conexión compartida (`StaticPool`) y
`PRAGMA foreign_keys=ON` en cada conexión. Compartido entre los
contratos de TaskListRepository/TaskRepository y el test de borrado en
cascada, para no duplicar esta configuración."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.sqlalchemy_task_list_repository import (
    SqlAlchemyTaskListRepository,
)
from app.infrastructure.persistence.sqlalchemy_task_repository import (
    SqlAlchemyTaskRepository,
)


def create_in_memory_sqlite_engine() -> Engine:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    return engine


def create_sqlalchemy_repositories() -> (
    tuple[SqlAlchemyTaskListRepository, SqlAlchemyTaskRepository]
):
    """Motor SQLite en memoria con las tablas creadas y ambos
    repositorios SQLAlchemy listos, compartiendo la misma sesión."""
    engine = create_in_memory_sqlite_engine()
    Base.metadata.create_all(engine)
    session = Session(engine)
    return SqlAlchemyTaskListRepository(session), SqlAlchemyTaskRepository(session)
