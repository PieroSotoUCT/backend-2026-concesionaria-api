"""Consultas de vehiculos sobre las colecciones compartidas."""

from app.repositories import datos


def asignar_id() -> int:
    return datos.siguiente_id("vehiculos")


def listar() -> list[dict[str, object]]:
    return [dict(registro) for registro in datos.vehiculos.values()]


def obtener(id: int) -> dict[str, object] | None:
    registro = datos.vehiculos.get(id)
    return dict(registro) if registro is not None else None


def guardar(registro: dict[str, object]) -> None:
    # Guardar una copia evita modificar la memoria por accidente desde otra capa.
    datos.vehiculos[registro["id"]] = dict(registro)


def eliminar(id: int) -> None:
    del datos.vehiculos[id]


def sucursal_existe(sucursal_id: int) -> bool:
    return sucursal_id in datos.sucursales


def tiene_historial_reservas(vehiculo_id: int) -> bool:
    return any(
        reserva["vehiculo_id"] == vehiculo_id
        for reserva in datos.reservas.values()
    )


def tiene_reserva_activa(vehiculo_id: int) -> bool:
    return any(
        reserva["vehiculo_id"] == vehiculo_id and reserva["estado"] == "activa"
        for reserva in datos.reservas.values()
    )
