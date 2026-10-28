"""Operaciones transaccionales de sucursales."""

from sqlalchemy import select

from app.db import SessionLocal, initialize_database
from app.errores import ErrorAplicacion
from app.models import Sucursal
from app.schemas.sucursal import SucursalCrear

initialize_database()


def _registro(sucursal: Sucursal) -> dict[str, object]:
    return {campo: getattr(sucursal, campo) for campo in
            ("id", "nombre", "direccion", "ciudad", "telefono", "horario_atencion")}


def crear_sucursal(entrada: SucursalCrear) -> dict[str, object]:
    with SessionLocal.begin() as session:
        sucursal = Sucursal(**entrada.model_dump())
        session.add(sucursal)
        session.flush()
        return _registro(sucursal)


def listar_sucursales() -> list[dict[str, object]]:
    with SessionLocal() as session:
        return [_registro(sucursal) for sucursal in
                session.scalars(select(Sucursal).order_by(Sucursal.id))]


def obtener_sucursal(id: int) -> dict[str, object]:
    with SessionLocal() as session:
        sucursal = session.get(Sucursal, id)
        if sucursal is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La sucursal no existe")
        return _registro(sucursal)
