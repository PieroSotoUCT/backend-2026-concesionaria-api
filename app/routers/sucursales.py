"""Rutas HTTP de sucursales."""

from fastapi import APIRouter, Path, status

from app.schemas.sucursal import SucursalCrear, SucursalRespuesta
from app.services import sucursales as servicio

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=SucursalRespuesta,
    summary="Registrar una sucursal",
    description="Crea una sucursal nueva. El ID lo asigna el servidor.",
    responses={
        201: {"description": "Sucursal creada correctamente."},
        422: {"description": "Los datos enviados no son válidos."},
    },
)
def crear_sucursal(entrada: SucursalCrear) -> dict[str, object]:
    """Registra una sucursal nueva."""
    return servicio.crear_sucursal(entrada)


@router.get(
    "",
    response_model=list[SucursalRespuesta],
    summary="Listar sucursales",
    description="Devuelve todas las sucursales registradas.",
    responses={
        200: {"description": "Lista de sucursales."},
    },
)
def listar_sucursales() -> list[dict[str, object]]:
    """Lista todas las sucursales."""
    return servicio.listar_sucursales()


@router.get(
    "/{id}",
    response_model=SucursalRespuesta,
    summary="Obtener sucursal por ID",
    description="Busca una sucursal usando su identificador.",
    responses={
        200: {"description": "Sucursal encontrada."},
        404: {"description": "No existe una sucursal con ese ID."},
        422: {"description": "El ID debe ser un entero positivo."},
    },
)
def obtener_sucursal(
    id: int = Path(gt=0, description="ID positivo de la sucursal"),
) -> dict[str, object]:
    """Obtiene una sucursal por su ID."""
    return servicio.obtener_sucursal(id)
