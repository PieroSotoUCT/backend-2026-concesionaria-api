"""Operaciones transaccionales y reglas de negocio de clientes."""

from sqlalchemy.exc import IntegrityError

from app.db import SessionLocal, initialize_database
from app.errores import ErrorAplicacion
from app.models import Cliente
from app.repositories import clientes as repositorio_clientes
from app.schemas.clientes import ClienteCrear

initialize_database()


def _registro(cliente: Cliente) -> dict[str, object]:
    """Convierte un modelo ORM en un diccionario de respuesta."""
    return {
        campo: getattr(cliente, campo)
        for campo in (
            "id",
            "rut",
            "nombre",
            "correo",
            "telefono",
            "direccion",
        )
    }


def _normalizar_rut(rut: str) -> str:
    """Elimina puntos y espacios, y convierte el RUT a mayúsculas."""
    return rut.replace(".", "").replace(" ", "").upper()


def _es_rut_duplicado(error: IntegrityError) -> bool:
    """Identifica una violación de unicidad de la columna RUT."""
    mensaje = str(error.orig).lower()
    return "unique constraint failed" in mensaje and "clientes.rut" in mensaje


def crear_cliente(entrada: ClienteCrear) -> dict[str, object]:
    """Valida las reglas de negocio y registra un cliente."""
    rut = _normalizar_rut(entrada.rut)

    if not rut:
        raise ErrorAplicacion(
            400,
            "BUSINESS_RULE_VIOLATION",
            "El RUT del cliente no puede estar vacío.",
        )

    try:
        with SessionLocal.begin() as session:
            cliente_existente = repositorio_clientes.buscar_por_rut(session, rut)

            if cliente_existente is not None:
                raise ErrorAplicacion(
                    409,
                    "DUPLICATE_RESOURCE",
                    f"Ya existe un cliente registrado con el RUT {rut}.",
                )

            cliente = Cliente(
                rut=rut,
                nombre=entrada.nombre,
                correo=str(entrada.correo),
                telefono=entrada.telefono,
                direccion=entrada.direccion,
            )

            repositorio_clientes.guardar(session, cliente)
            session.flush()

            return _registro(cliente)

    except IntegrityError as error:
        if not _es_rut_duplicado(error):
            raise

        raise ErrorAplicacion(
            409,
            "DUPLICATE_RESOURCE",
            f"Ya existe un cliente registrado con el RUT {rut}.",
        ) from error


def listar_clientes() -> list[dict[str, object]]:
    """Devuelve todos los clientes registrados."""
    with SessionLocal() as session:
        clientes = repositorio_clientes.listar(session)
        return [_registro(cliente) for cliente in clientes]


def obtener_cliente(cliente_id: int) -> dict[str, object]:
    """Busca un cliente por su identificador."""
    with SessionLocal() as session:
        cliente = repositorio_clientes.obtener(session, cliente_id)

        if cliente is None:
            raise ErrorAplicacion(
                404,
                "RESOURCE_NOT_FOUND",
                f"No existe un cliente con ID {cliente_id}.",
            )

        return _registro(cliente)
