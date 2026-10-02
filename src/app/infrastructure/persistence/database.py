"""Configuración de SQLAlchemy: engine, fábrica de sesiones y Base
declarativa (A5: síncrono; A10: la URL viene de `Settings`).

No se llama `Base.metadata.create_all()` desde la aplicación (A6): el
esquema se gestiona con Alembic. `create_all()` solo se usa en tests
contra SQLite en memoria.
"""

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


class Base(DeclarativeBase):
    """Base declarativa de los modelos ORM
    (`infrastructure/persistence/models.py`)."""


def create_sqlalchemy_engine(database_url: str) -> Engine:
    return create_engine(database_url)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
