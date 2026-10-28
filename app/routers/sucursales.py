"""Rutas HTTP de sucursales."""

from fastapi import APIRouter, Path

from app.schemas.sucursal import SucursalCrear, SucursalRespuesta
from app.services import sucursales as servicio

router = APIRouter(prefix="/sucursales", tags=["Sucursales"])


@router.post("", status_code=201, response_model=SucursalRespuesta)
def crear_sucursal(entrada: SucursalCrear) -> dict[str, object]:
    return servicio.crear_sucursal(entrada)


@router.get("", response_model=list[SucursalRespuesta])
def listar_sucursales() -> list[dict[str, object]]:
    return servicio.listar_sucursales()


@router.get("/{id}", response_model=SucursalRespuesta)
def obtener_sucursal(id: int = Path(gt=0)) -> dict[str, object]:
    return servicio.obtener_sucursal(id)
