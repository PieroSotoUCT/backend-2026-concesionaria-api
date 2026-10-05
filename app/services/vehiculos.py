"""Operaciones y reglas de negocio del modulo de vehiculos."""

from app.domain.vehiculo import EstadoVehiculo, Vehiculo
from app.errores import ErrorAplicacion
from app.repositories import vehiculos as repositorio
from app.schemas.vehiculo import VehiculoActualizar, VehiculoCrear


def comprobar_sucursal(sucursal_id: int) -> None:
    if not repositorio.sucursal_existe(sucursal_id):
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La sucursal no existe")


def crear_vehiculo(entrada: VehiculoCrear) -> dict[str, object]:
    comprobar_sucursal(entrada.sucursal_id)
    vehiculo = Vehiculo(
        id=repositorio.asignar_id(),
        estado=EstadoVehiculo.DISPONIBLE,
        **entrada.model_dump(),
    )
    registro = vehiculo.a_registro()
    repositorio.guardar(registro)
    return registro


def listar_vehiculos() -> list[dict[str, object]]:
    return sorted(repositorio.listar(), key=lambda vehiculo: vehiculo["id"])


def obtener_vehiculo(id: int) -> dict[str, object]:
    vehiculo = repositorio.obtener(id)
    if vehiculo is None:
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
    return vehiculo


def actualizar_vehiculo(id: int, entrada: VehiculoActualizar) -> dict[str, object]:
    vehiculo = obtener_vehiculo(id)
    cambios = entrada.model_dump(mode="json", exclude_unset=True)
    comprobar_sucursal(cambios.get("sucursal_id", vehiculo["sucursal_id"]))

    if "estado" in cambios:
        if cambios["estado"] != "vendido":
            raise ErrorAplicacion(
                400,
                "STATE_MANAGED_BY_RESERVATIONS",
                "Solo se permite marcar vendido; reservas controla reservar y liberar",
            )
        if vehiculo["estado"] != "disponible" or repositorio.tiene_reserva_activa(id):
            raise ErrorAplicacion(
                409,
                "STATE_CONFLICT",
                "Solo puede venderse un vehiculo disponible y sin reserva activa",
            )

    # Todas las comprobaciones ocurren antes de guardar: un error no aplica
    # parcialmente el precio, la sucursal ni ningun otro campo de la solicitud.
    vehiculo.update(cambios)
    repositorio.guardar(vehiculo)
    return vehiculo


def eliminar_vehiculo(id: int) -> None:
    obtener_vehiculo(id)
    if repositorio.tiene_historial_reservas(id):
        raise ErrorAplicacion(
            409,
            "RESERVATION_HISTORY_CONFLICT",
            "No se puede eliminar un vehiculo con historial de reservas",
        )
    repositorio.eliminar(id)
