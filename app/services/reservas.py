"""Operaciones y reglas de negocio del modulo de reservas."""

from datetime import date

from app.domain.reserva import EstadoReserva, Reserva
from app.errores import ErrorAplicacion
from app.repositories import reservas as repositorio
from app.schemas.reserva import ReservaCrear


def procesar_vencimientos(hoy: date | None = None) -> int:
    """Marca como vencidas las reservas activas con fecha_vencimiento < hoy.

    Libera cada vehiculo que quedo reservado por ellas y devuelve cuantas
    reservas vencieron. Usa la fecha local del servidor (date.today()), como
    indica CONTRATO.md; el parametro existe para poder probar fechas concretas.
    """
    hoy = hoy if hoy is not None else date.today()
    vencidas = 0
    for reserva in repositorio.listar_activas():
        if reserva["fecha_vencimiento"] >= hoy:
            continue
        reserva["estado"] = EstadoReserva.VENCIDA.value
        repositorio.guardar(reserva)
        _liberar_vehiculo(reserva)
        vencidas += 1
    return vencidas


def _liberar_vehiculo(reserva: dict[str, object]) -> None:
    """Devuelve el vehiculo a disponible si estaba reservado y nadie mas lo reserva."""
    vehiculo = repositorio.obtener_vehiculo(reserva["vehiculo_id"])
    if vehiculo is None or vehiculo["estado"] != "reservado":
        return
    if repositorio.tiene_otra_reserva_activa(vehiculo["id"], reserva["id"]):
        return
    repositorio.cambiar_estado_vehiculo(vehiculo["id"], "disponible")


def crear_reserva(entrada: ReservaCrear) -> dict[str, object]:
    procesar_vencimientos()
    if not repositorio.cliente_existe(entrada.cliente_id):
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El cliente no existe")
    vehiculo = repositorio.obtener_vehiculo(entrada.vehiculo_id)
    if vehiculo is None:
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")

    hoy = date.today()
    if entrada.fecha_vencimiento < hoy:
        raise ErrorAplicacion(
            400,
            "INVALID_EXPIRATION_DATE",
            "La fecha de vencimiento no puede ser anterior a hoy",
        )
    if vehiculo["estado"] != "disponible":
        raise ErrorAplicacion(
            409,
            "VEHICLE_NOT_AVAILABLE",
            "Solo se puede reservar un vehiculo disponible",
        )

    # Todas las comprobaciones ocurren antes de escribir: un error no deja
    # una reserva creada ni un vehiculo a medio actualizar.
    reserva = Reserva(
        id=repositorio.asignar_id(),
        cliente_id=entrada.cliente_id,
        vehiculo_id=entrada.vehiculo_id,
        fecha_reserva=hoy,
        fecha_vencimiento=entrada.fecha_vencimiento,
        monto_reserva=entrada.monto_reserva,
        estado=EstadoReserva.ACTIVA,
    )
    registro = reserva.a_registro()
    repositorio.guardar(registro)
    repositorio.cambiar_estado_vehiculo(entrada.vehiculo_id, "reservado")
    return registro


def listar_reservas() -> list[dict[str, object]]:
    procesar_vencimientos()
    return sorted(repositorio.listar(), key=lambda reserva: reserva["id"])


def obtener_reserva(id: int) -> dict[str, object]:
    procesar_vencimientos()
    reserva = repositorio.obtener(id)
    if reserva is None:
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La reserva no existe")
    return reserva


def cancelar_reserva(id: int) -> dict[str, object]:
    reserva = obtener_reserva(id)  # tambien procesa vencimientos
    if reserva["estado"] != EstadoReserva.ACTIVA.value:
        raise ErrorAplicacion(
            409,
            "STATE_CONFLICT",
            f"Solo se puede cancelar una reserva activa; esta {reserva['estado']}",
        )
    reserva["estado"] = EstadoReserva.CANCELADA.value
    repositorio.guardar(reserva)
    _liberar_vehiculo(reserva)
    return reserva
