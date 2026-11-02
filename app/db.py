"""Configuracion de la base de datos y sesiones SQLAlchemy."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv(
    "CONCESIONARIA_DATABASE_URL",
    "sqlite:///./concesionaria.db",
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)


if engine.dialect.name == "sqlite":
    @event.listens_for(engine, "connect")
    def _activar_claves_foraneas(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    """Entrega una sesion para integraciones que necesiten inyeccion."""
    with SessionLocal() as session:
        yield session


def initialize_database() -> None:
    """Compatibilidad temporal: el esquema se prepara con Alembic, no al importar."""
