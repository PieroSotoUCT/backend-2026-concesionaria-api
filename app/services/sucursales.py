
"""Operaciones transaccionales y reglas de negocio de sucursales."""

from app.db import SessionLocal, initialize_database
from app.errores import ErrorAplicacion
from app.models import Sucursal
from app.repositories import sucursales as repositorio_sucursales
from app.schemas.sucursal import SucursalCrear

initialize_database()


def _registro(sucursal: Sucursal) -> dict[str, object]:
    """Convierte una sucursal ORM en un diccionario de respuesta."""
    return {
        campo: getattr(sucursal, campo)
        for campo in (
            "id",
            "nombre",
            "direccion",
            "ciudad",
            "telefono",
            "horario_atencion",
        )
    }


def crear_sucursal(entrada: SucursalCrear) -> dict[str, object]:
    """Registra una nueva sucursal."""
    with SessionLocal.begin() as session:
        sucursal = Sucursal(**entrada.model_dump())

        repositorio_sucursales.guardar(session, sucursal)
        session.flush()

        return _registro(sucursal)


def listar_sucursales() -> list[dict[str, object]]:
    """Devuelve todas las sucursales registradas."""
    with SessionLocal() as session:
        sucursales = repositorio_sucursales.listar(session)
        return [_registro(sucursal) for sucursal in sucursales]


def obtener_sucursal(sucursal_id: int) -> dict[str, object]:
    """Busca una sucursal por su ID."""
    with SessionLocal() as session:
        sucursal = repositorio_sucursales.obtener(session, sucursal_id)

        if sucursal is None:
            raise ErrorAplicacion(
                404,
                "RESOURCE_NOT_FOUND",
                f"No existe una sucursal con ID {sucursal_id}.",
            )

        return _registro(sucursal)
