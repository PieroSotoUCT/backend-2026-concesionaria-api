"""Rutas HTTP para la gestión de sucursales."""

from fastapi import APIRouter, status

from app.schemas.sucursal import SucursalCrear, SucursalRespuesta
from app.services import sucursales as servicio_sucursales

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.post("", response_model=SucursalRespuesta, status_code=status.HTTP_201_CREATED)
def crear_sucursal(datos: SucursalCrear) -> dict[str, object]:
    """Registra una sucursal nueva."""
    return servicio_sucursales.crear_sucursal(datos.model_dump())


@router.get("", response_model=list[SucursalRespuesta])
def listar_sucursales() -> list[dict[str, object]]:
    """Lista todas las sucursales."""
    return servicio_sucursales.listar_sucursales()


@router.get("/{sucursal_id}", response_model=SucursalRespuesta)
def obtener_sucursal(sucursal_id: int) -> dict[str, object]:
    """Obtiene una sucursal por su ID."""
    return servicio_sucursales.obtener_sucursal(sucursal_id)
