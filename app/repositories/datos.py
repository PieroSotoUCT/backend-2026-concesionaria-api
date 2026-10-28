"""Compatibilidad para inicializacion de la base ORM.

Las rutas y servicios no usan colecciones en memoria. Este modulo conserva
solo el punto de importacion historico y ya no expone registros mutables.
"""

from app.db import initialize_database


def siguiente_id(_nombre_coleccion: str) -> int:
    raise RuntimeError("Los IDs son asignados por la base de datos")


def limpiar_base() -> None:
    """Elimina registros mediante una transaccion, principalmente para tests."""
    from app.db import SessionLocal
    from app.models import Cliente, Reserva, Sucursal, Vehiculo

    with SessionLocal.begin() as session:
        for modelo in (Reserva, Vehiculo, Cliente, Sucursal):
            session.query(modelo).delete()


initialize_database()
