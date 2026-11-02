
"""Consultas ORM para la gestión de sucursales."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Sucursal


def listar(session: Session) -> list[Sucursal]:
    """Obtiene todas las sucursales ordenadas por ID."""
    return list(session.scalars(select(Sucursal).order_by(Sucursal.id)))


def obtener(session: Session, sucursal_id: int) -> Sucursal | None:
    """Busca una sucursal por su ID."""
    return session.get(Sucursal, sucursal_id)


def guardar(session: Session, sucursal: Sucursal) -> None:
    """Agrega una sucursal a la sesión de base de datos."""
    session.add(sucursal)
