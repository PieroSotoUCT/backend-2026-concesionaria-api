"""Servicio con las reglas de negocio para las sucursales."""

from app.domain.sucursal import Sucursal
from app.errores import ErrorAplicacion
from app.repositories import sucursales as repositorio_sucursales


def listar_sucursales() -> list[dict[str, object]]:
    """Devuelve todas las sucursales registradas."""
    return repositorio_sucursales.listar()


def obtener_sucursal(sucursal_id: int) -> dict[str, object]:
    """Busca una sucursal por su ID."""
    sucursal = repositorio_sucursales.obtener(sucursal_id)

    if sucursal is None:
        raise ErrorAplicacion(
            estado_http=404,
            codigo="RESOURCE_NOT_FOUND",
            mensaje=f"No existe una sucursal con ID {sucursal_id}.",
            detalles=[],
        )

    return sucursal


def crear_sucursal(datos: dict[str, str]) -> dict[str, object]:
    """Registra una sucursal nueva."""
    sucursal = Sucursal(
        id=repositorio_sucursales.asignar_id(),
        nombre=datos["nombre"],
        direccion=datos["direccion"],
        ciudad=datos["ciudad"],
        telefono=datos["telefono"],
        horario_atencion=datos["horario_atencion"],
    )

    registro = sucursal.a_registro()
    repositorio_sucursales.guardar(registro)

    return registro
