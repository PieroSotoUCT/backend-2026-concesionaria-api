
"""Consultas ORM para la gestión de clientes."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cliente


def listar(session: Session) -> list[Cliente]:
    """Obtiene todos los clientes ordenados por ID."""
    return list(session.scalars(select(Cliente).order_by(Cliente.id)))


def obtener(session: Session, cliente_id: int) -> Cliente | None:
    """Busca un cliente por su ID."""
    return session.get(Cliente, cliente_id)


def buscar_por_rut(session: Session, rut: str) -> Cliente | None:
    """Busca un cliente por su RUT."""
    return session.scalar(
        select(Cliente).where(Cliente.rut == rut)
    )


def guardar(session: Session, cliente: Cliente) -> None:
    """Agrega un cliente a la sesión de base de datos."""
    session.add(cliente)
