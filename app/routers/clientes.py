"""Rutas HTTP de clientes."""

from fastapi import APIRouter, Path

from app.schemas.clientes import ClienteCrear, ClienteRespuesta
from app.services import clientes as servicio

router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", status_code=201, response_model=ClienteRespuesta)
def crear_cliente(entrada: ClienteCrear) -> dict[str, object]:
    return servicio.crear_cliente(entrada)


@router.get("", response_model=list[ClienteRespuesta])
def listar_clientes() -> list[dict[str, object]]:
    return servicio.listar_clientes()


@router.get("/{id}", response_model=ClienteRespuesta)
def obtener_cliente(id: int = Path(gt=0)) -> dict[str, object]:
    return servicio.obtener_cliente(id)
