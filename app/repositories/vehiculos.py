"""Consultas ORM de vehiculos y sus relaciones."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Reserva, Sucursal, Vehiculo


def listar(session: Session) -> list[Vehiculo]:
    return list(session.scalars(select(Vehiculo).order_by(Vehiculo.id)))


def consultar(
    session: Session, *, marca: str | None, estado: str | None,
    sucursal_id: int | None, precio_min: int | None, precio_max: int | None,
    ordenar_por: str | None, direccion: str, pagina: int, limite: int,
) -> tuple[list[Vehiculo], int]:
    consulta = select(Vehiculo)
    if estado is not None:
        consulta = consulta.where(Vehiculo.estado == estado)
    if sucursal_id is not None:
        consulta = consulta.where(Vehiculo.sucursal_id == sucursal_id)
    if precio_min is not None:
        consulta = consulta.where(Vehiculo.precio >= precio_min)
    if precio_max is not None:
        consulta = consulta.where(Vehiculo.precio <= precio_max)
    encontrados = list(session.scalars(consulta))
    if marca is not None:
        encontrados = [vehiculo for vehiculo in encontrados
                      if vehiculo.marca.strip().casefold() == marca.casefold()]

    # La ordenacion estable conserva el ID ascendente cuando hay empates.
    encontrados.sort(key=lambda vehiculo: vehiculo.id)
    if ordenar_por is not None:
        encontrados.sort(key=lambda vehiculo: getattr(vehiculo, ordenar_por),
                         reverse=direccion == "desc")
    total = len(encontrados)
    inicio = (pagina - 1) * limite
    return encontrados[inicio:inicio + limite], total


def obtener(session: Session, id: int) -> Vehiculo | None:
    return session.get(Vehiculo, id)


def guardar(session: Session, vehiculo: Vehiculo) -> None:
    session.add(vehiculo)
    session.flush()


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
