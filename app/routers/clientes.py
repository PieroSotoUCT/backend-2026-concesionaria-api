"""Rutas HTTP para la gestión de clientes."""



from fastapi import APIRouter, status

from app.schemas.cliente import ClienteCrear, ClienteRespuesta
from app.services import clientes as servicio_clientes


router = APIRouter(prefix="/clientes", tags=["Clientes"])


@router.post("", response_model=ClienteRespuesta, status_code=status.HTTP_201_CREATED)
def crear_cliente(datos: ClienteCrear) -> dict[str, object]:
    return servicio_clientes.crear_cliente(datos.model_dump())



@router.get("", response_model=list[ClienteRespuesta])
def listar_cliente() -> list[dict[str, object]]:
    return servicio_clientes.listar_clientes()


@router.get("/{cliente_id}", response_model=ClienteRespuesta)
def obtener_cliente(cliente_id: int) -> dict[str, object]:
    return servicio_clientes.obtener_cliente(cliente_id)



