"""Configuración de SQLAlchemy: engine, fábrica de sesiones y Base
declarativa (A5: síncrono; A10: la URL viene de `Settings`).

No se llama `Base.metadata.create_all()` desde la aplicación (A6): el
esquema se gestiona con Alembic. `create_all()` solo se usa en tests
contra SQLite en memoria.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base declarativa de los modelos ORM
    (`infrastructure/persistence/models.py`)."""


def create_sqlalchemy_engine(database_url: str) -> Engine:
    engine = create_engine(database_url)

    if database_url.startswith("sqlite"):
        # Sin esto, SQLite no aplica las FK (A9): ON DELETE CASCADE
        # (B8) no funcionaría. PostgreSQL las aplica por defecto.
        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
