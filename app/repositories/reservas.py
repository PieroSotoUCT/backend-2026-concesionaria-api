"""Consultas de reservas sobre las colecciones compartidas."""

from app.repositories import datos


def asignar_id() -> int:
    return datos.siguiente_id("reservas")


def listar() -> list[dict[str, object]]:
    return [dict(registro) for registro in datos.reservas.values()]


def listar_activas() -> list[dict[str, object]]:
    return [
        dict(registro)
        for registro in datos.reservas.values()
        if registro["estado"] == "activa"
    ]


def obtener(id: int) -> dict[str, object] | None:
    registro = datos.reservas.get(id)
    return dict(registro) if registro is not None else None


def guardar(registro: dict[str, object]) -> None:
    # Guardar una copia evita modificar la memoria por accidente desde otra capa.
    datos.reservas[registro["id"]] = dict(registro)


def cliente_existe(cliente_id: int) -> bool:
    return cliente_id in datos.clientes


def obtener_vehiculo(vehiculo_id: int) -> dict[str, object] | None:
    registro = datos.vehiculos.get(vehiculo_id)
    return dict(registro) if registro is not None else None


def cambiar_estado_vehiculo(vehiculo_id: int, estado: str) -> None:
    """Unico punto donde reservas escribe el estado de un vehiculo."""
    datos.vehiculos[vehiculo_id]["estado"] = estado


def tiene_otra_reserva_activa(vehiculo_id: int, excepto_id: int) -> bool:
    return any(
        reserva["vehiculo_id"] == vehiculo_id
        and reserva["estado"] == "activa"
        and reserva["id"] != excepto_id
        for reserva in datos.reservas.values()
    )
