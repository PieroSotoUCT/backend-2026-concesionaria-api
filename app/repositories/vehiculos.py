"""Consultas ORM de vehiculos y sus relaciones."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Reserva, Sucursal, Vehiculo


def listar(session: Session) -> list[Vehiculo]:
    return list(session.scalars(select(Vehiculo).order_by(Vehiculo.id)))


def obtener(session: Session, id: int) -> Vehiculo | None:
    return session.get(Vehiculo, id)


def eliminar(session: Session, vehiculo: Vehiculo) -> None:
    session.delete(vehiculo)


def sucursal_existe(session: Session, sucursal_id: int) -> bool:
    return session.get(Sucursal, sucursal_id) is not None


def tiene_historial_reservas(session: Session, vehiculo_id: int) -> bool:
    return session.scalar(
        select(Reserva.id).where(Reserva.vehiculo_id == vehiculo_id).limit(1)
    ) is not None


def tiene_reserva_activa(session: Session, vehiculo_id: int) -> bool:
    return session.scalar(
        select(Reserva.id).where(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado == "activa",
        ).limit(1)
    ) is not None
