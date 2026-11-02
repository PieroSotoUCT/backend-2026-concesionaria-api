"""Operaciones transaccionales del modulo de reservas."""

from datetime import date

from sqlalchemy.orm import Session

from app.db import SessionLocal, initialize_database
from app.domain.reserva import EstadoReserva
from app.errores import ErrorAplicacion
from app.models import Reserva
from app.repositories import reservas as repositorio
from app.schemas.reserva import ReservaCrear

initialize_database()


def _registro(reserva: Reserva) -> dict[str, object]:
    return {
        "id": reserva.id, "cliente_id": reserva.cliente_id,
        "vehiculo_id": reserva.vehiculo_id, "fecha_reserva": reserva.fecha_reserva,
        "fecha_vencimiento": reserva.fecha_vencimiento,
        "monto_reserva": reserva.monto_reserva, "estado": reserva.estado,
    }


def procesar_vencimientos_en_sesion(session: Session, hoy: date | None = None) -> int:
    """Actualiza vencimientos en la transaccion que confirma el llamador."""
    hoy = hoy or date.today()
    vencidas = repositorio.listar_vencidas(session, hoy)
    for reserva in vencidas:
        reserva.estado = EstadoReserva.VENCIDA.value
    session.flush()
    for reserva in vencidas:
        _liberar_vehiculo(session, reserva)
    return len(vencidas)


def procesar_vencimientos(hoy: date | None = None) -> int:
    """Procesa vencimientos y confirma una transaccion independiente."""
    with SessionLocal.begin() as session:
        return procesar_vencimientos_en_sesion(session, hoy)


def _liberar_vehiculo(session, reserva: Reserva) -> None:
    vehiculo = repositorio.obtener_vehiculo(session, reserva.vehiculo_id)
    if vehiculo is None or vehiculo.estado != "reservado":
        return
    if not repositorio.tiene_otra_reserva_activa(session, vehiculo.id, reserva.id):
        vehiculo.estado = "disponible"


def crear_reserva(entrada: ReservaCrear) -> dict[str, object]:
    with SessionLocal.begin() as session:
        procesar_vencimientos_en_sesion(session)
        if not repositorio.cliente_existe(session, entrada.cliente_id):
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El cliente no existe")
        vehiculo = repositorio.obtener_vehiculo(session, entrada.vehiculo_id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        hoy = date.today()
        if entrada.fecha_vencimiento < hoy:
            raise ErrorAplicacion(400, "INVALID_EXPIRATION_DATE",
                                  "La fecha de vencimiento no puede ser anterior a hoy")
        if (vehiculo.estado != "disponible"
                or repositorio.tiene_reserva_activa(session, vehiculo.id)):
            raise ErrorAplicacion(409, "VEHICLE_NOT_AVAILABLE",
                                  "Solo se puede reservar un vehiculo disponible "
                                  "y sin otra reserva activa")
        reserva = Reserva(
            cliente_id=entrada.cliente_id, vehiculo_id=entrada.vehiculo_id,
            fecha_reserva=hoy, fecha_vencimiento=entrada.fecha_vencimiento,
            monto_reserva=entrada.monto_reserva, estado=EstadoReserva.ACTIVA.value,
        )
        session.add(reserva)
        vehiculo.estado = "reservado"
        session.flush()
        return _registro(reserva)


def listar_reservas() -> list[dict[str, object]]:
    with SessionLocal.begin() as session:
        procesar_vencimientos_en_sesion(session)
        return [_registro(reserva) for reserva in repositorio.listar(session)]


def obtener_reserva(id: int) -> dict[str, object]:
    with SessionLocal.begin() as session:
        procesar_vencimientos_en_sesion(session)
        reserva = repositorio.obtener(session, id)
        if reserva is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La reserva no existe")
        return _registro(reserva)


def cancelar_reserva(id: int) -> dict[str, object]:
    with SessionLocal.begin() as session:
        procesar_vencimientos_en_sesion(session)
        reserva = repositorio.obtener(session, id)
        if reserva is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La reserva no existe")
        if reserva.estado != EstadoReserva.ACTIVA.value:
            raise ErrorAplicacion(409, "STATE_CONFLICT",
                                  f"Solo se puede cancelar una reserva activa; esta {reserva.estado}")
        reserva.estado = EstadoReserva.CANCELADA.value
        _liberar_vehiculo(session, reserva)
        session.flush()
        return _registro(reserva)
