
"""Repositorio para gestionar las sucursales de la concesionaria."""

from app.repositories import datos


def asignar_id() -> int:
    """Obtiene un nuevo ID para una sucursal."""
    return datos.siguiente_id("sucursales")


def listar() -> list[dict[str, object]]:
    """Devuelve todas las sucursales registradas."""
    return [dict(registro) for registro in datos.sucursales.values()]


def obtener(sucursal_id: int) -> dict[str, object] | None:
    """Busca una sucursal por su ID."""
    registro = datos.sucursales.get(sucursal_id)
    return dict(registro) if registro is not None else None


def guardar(registro: dict[str, object]) -> None:
    """Guarda una sucursal en el almacenamiento compartido."""
    datos.sucursales[registro["id"]] = dict(registro)
