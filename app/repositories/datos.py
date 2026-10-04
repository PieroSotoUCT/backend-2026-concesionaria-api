"""Colecciones compartidas por los modulos del equipo.

Los registros usan las claves descritas en CONTRATO.md. Al reiniciar el
proceso se pierden todos los datos y los contadores vuelven a cero.
"""

vehiculos: dict[int, dict[str, object]] = {}
sucursales: dict[int, dict[str, object]] = {}
clientes: dict[int, dict[str, object]] = {}
reservas: dict[int, dict[str, object]] = {}

contadores = {
    "vehiculos": 0,
    "sucursales": 0,
    "clientes": 0,
    "reservas": 0,
}


def siguiente_id(nombre_coleccion: str) -> int:
    """Asigna un ID nuevo sin reutilizar los eliminados."""
    contadores[nombre_coleccion] += 1
    return contadores[nombre_coleccion]
