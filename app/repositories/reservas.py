"""Consultas ORM de reservas y relaciones de disponibilidad."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Cliente, Reserva, Vehiculo


def listar(session: Session) -> list[Reserva]:
    return list(session.scalars(select(Reserva).order_by(Reserva.id)))


def listar_activas(session: Session) -> list[Reserva]:
    return list(session.scalars(select(Reserva).where(Reserva.estado == "activa")))


def obtener(session: Session, id: int) -> Reserva | None:
    return session.get(Reserva, id)


def cliente_existe(session: Session, cliente_id: int) -> bool:
    return session.get(Cliente, cliente_id) is not None


def obtener_vehiculo(session: Session, vehiculo_id: int) -> Vehiculo | None:
    return session.get(Vehiculo, vehiculo_id)


def tiene_otra_reserva_activa(session: Session, vehiculo_id: int, excepto_id: int) -> bool:
    return session.scalar(
        select(Reserva.id).where(
            Reserva.vehiculo_id == vehiculo_id,
            Reserva.estado == "activa",
            Reserva.id != excepto_id,
        ).limit(1)
    ) is not None
