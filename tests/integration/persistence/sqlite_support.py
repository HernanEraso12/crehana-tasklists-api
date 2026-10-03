"""Motor de BD para las suites de integración de persistencia y de
API. Por defecto, SQLite en memoria: una sola conexión compartida
(`StaticPool`, A9) y `PRAGMA foreign_keys=ON` en cada conexión.

Si la variable de entorno `TEST_DATABASE_URL` está definida (el job
`tests-postgres` del CI la pone apuntando a un PostgreSQL real, A7),
se usa esa BD en su lugar. En local, sin la variable, nada cambia.
"""

import os

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from app.infrastructure.persistence.database import (
    Base,
    create_sqlalchemy_engine,
)
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


def create_test_engine() -> Engine:
    """SQLite en memoria por defecto; PostgreSQL real si
    `TEST_DATABASE_URL` está definida (CI, job `tests-postgres`)."""
    test_database_url = os.environ.get("TEST_DATABASE_URL")
    if test_database_url:
        return create_sqlalchemy_engine(test_database_url)
    return create_in_memory_sqlite_engine()


def create_sqlalchemy_repositories() -> (
    tuple[SqlAlchemyTaskListRepository, SqlAlchemyTaskRepository]
):
    """Motor de test (SQLite en memoria o Postgres real, según
    `TEST_DATABASE_URL`) con el esquema recién creado (`drop_all` +
    `create_all`: aislamiento entre tests también contra una BD real
    compartida, donde una BD en memoria nueva no lo garantiza sola) y
    ambos repositorios SQLAlchemy listos, compartiendo la misma
    sesión.

    Quien llame a esta función es responsable de cerrar la sesión y
    liberar el motor al terminar (`dispose_sqlalchemy_repositories`):
    sin eso, contra Postgres real cada test deja una conexión abierta
    con una transacción sin terminar (los repositorios hacen
    `flush()`, no `commit()`; eso lo decide la capa API por request),
    y el siguiente test que intente `DROP TABLE` para limpiar el
    esquema queda bloqueado esperando ese lock. Con SQLite en memoria
    esto no se nota porque cada test tiene su propia BD descartable."""
    engine = create_test_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    session = Session(engine)
    return SqlAlchemyTaskListRepository(session), SqlAlchemyTaskRepository(session)


def dispose_sqlalchemy_repositories(
    task_list_repository: SqlAlchemyTaskListRepository,
) -> None:
    """Cierra la sesión (con `rollback` primero, por si quedó una
    transacción abierta) y libera el motor. Ver la nota en
    `create_sqlalchemy_repositories`."""
    session = task_list_repository.session
    session.rollback()
    session.close()
    session.bind.dispose()
