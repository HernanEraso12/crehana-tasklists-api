"""SQLite en memoria para las suites de contrato de persistencia (A9):
una sola conexión compartida (`StaticPool`) y `PRAGMA foreign_keys=ON`
en cada conexión. Compartido entre los contratos de TaskListRepository
y TaskRepository para no duplicar esta configuración."""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.pool import StaticPool


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
