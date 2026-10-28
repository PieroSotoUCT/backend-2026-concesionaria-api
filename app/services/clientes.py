"""Operaciones transaccionales de clientes."""

from sqlalchemy import select

from app.db import SessionLocal, initialize_database
from app.errores import ErrorAplicacion
from app.models import Cliente
from app.schemas.clientes import ClienteCrear

initialize_database()


def _registro(cliente: Cliente) -> dict[str, object]:
    return {campo: getattr(cliente, campo) for campo in
            ("id", "rut", "nombre", "correo", "telefono", "direccion")}


def _normalizar_rut(rut: str) -> str:
    return rut.replace(".", "").replace(" ", "").upper()


def crear_cliente(entrada: ClienteCrear) -> dict[str, object]:
    with SessionLocal.begin() as session:
        rut = _normalizar_rut(entrada.rut)
        if session.scalar(select(Cliente.id).where(Cliente.rut == rut)) is not None:
            raise ErrorAplicacion(409, "DUPLICATE_RUT", "El RUT ya esta registrado")
        cliente = Cliente(rut=rut, nombre=entrada.nombre, correo=entrada.correo,
                          telefono=entrada.telefono, direccion=entrada.direccion)
        session.add(cliente)
        session.flush()
        return _registro(cliente)


def listar_clientes() -> list[dict[str, object]]:
    with SessionLocal() as session:
        return [_registro(cliente) for cliente in
                session.scalars(select(Cliente).order_by(Cliente.id))]


def obtener_cliente(id: int) -> dict[str, object]:
    with SessionLocal() as session:
        cliente = session.get(Cliente, id)
        if cliente is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El cliente no existe")
        return _registro(cliente)
