"""Configuracion de la base de datos y sesiones SQLAlchemy."""

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv(
    "CONCESIONARIA_DATABASE_URL",
    "sqlite:///./concesionaria.db",
)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_session() -> Iterator[Session]:
    """Entrega una sesion para integraciones que necesiten inyeccion."""
    with SessionLocal() as session:
        yield session


def initialize_database() -> None:
    from app.models import Cliente, Reserva, Sucursal, Vehiculo  # noqa: F401

    Base.metadata.create_all(bind=engine)
