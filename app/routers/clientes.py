"""Rutas HTTP de clientes."""

from fastapi import APIRouter, Path, status

from app.schemas.clientes import ClienteCrear, ClienteRespuesta
from app.services import clientes as servicio

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=ClienteRespuesta,
    summary="Registrar un cliente",
    description="Crea un cliente nuevo. El ID lo asigna el servidor.",
    responses={
        201: {"description": "Cliente creado correctamente."},
        409: {"description": "Ya existe un cliente con ese RUT."},
        422: {"description": "Los datos enviados no son válidos."},
    },
)
def crear_cliente(entrada: ClienteCrear) -> dict[str, object]:
    """Registra un cliente nuevo."""
    return servicio.crear_cliente(entrada)


@router.get(
    "",
    response_model=list[ClienteRespuesta],
    summary="Listar clientes",
    description="Devuelve todos los clientes registrados.",
    responses={200: {"description": "Lista de clientes."}},
)
def listar_clientes() -> list[dict[str, object]]:
    """Lista todos los clientes."""
    return servicio.listar_clientes()


@router.get(
    "/{id}",
    response_model=ClienteRespuesta,
    summary="Obtener cliente por ID",
    description="Busca un cliente usando su identificador.",
    responses={
        200: {"description": "Cliente encontrado."},
        404: {"description": "No existe un cliente con ese ID."},
        422: {"description": "El ID debe ser un entero positivo."},
    },
)
def obtener_cliente(
    id: int = Path(gt=0, description="ID positivo del cliente"),
) -> dict[str, object]:
    """Obtiene un cliente por su ID."""
    return servicio.obtener_cliente(id)
