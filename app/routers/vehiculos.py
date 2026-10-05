"""Contrato HTTP de vehiculos; las reglas se delegan al servicio."""

from fastapi import APIRouter, Body, Path, Response

from app.schemas.error import ErrorRespuesta
from app.schemas.vehiculo import VehiculoActualizar, VehiculoCrear, VehiculoRespuesta
from app.services import vehiculos as servicio

router = APIRouter(prefix="/vehiculos", tags=["Vehiculos"])

EJEMPLO_VEHICULO = {
    "id": 1, "marca": "Toyota", "modelo": "Yaris", "anio": 2022,
    "precio": 10990000, "kilometraje": 23000, "transmision": "manual",
    "condicion": "usado", "estado": "disponible", "sucursal_id": 1,
}
ERROR_404 = {
    "model": ErrorRespuesta,
    "description": "El vehiculo o la sucursal solicitada no existe",
    "content": {"application/json": {"example": {"error": {
        "code": "RESOURCE_NOT_FOUND", "message": "El recurso no existe", "details": [],
    }}}},
}
ERROR_422 = {
    "model": ErrorRespuesta,
    "description": "Datos, campos adicionales o ID invalidos",
    "content": {"application/json": {"example": {"error": {
        "code": "VALIDATION_ERROR", "message": "Datos o parametros invalidos",
        "details": [{"campo": "body.precio", "mensaje": "Input should be greater than 0"}],
    }}}},
}


@router.post(
    "", status_code=201, response_model=VehiculoRespuesta,
    summary="Crear un vehiculo",
    description="Registra un vehiculo disponible en una sucursal existente. "
                "El servidor asigna su ID y estado; ambos se rechazan en la entrada.",
    responses={
        201: {"description": "Vehiculo creado", "content": {
            "application/json": {"example": EJEMPLO_VEHICULO}}},
        404: ERROR_404, 422: ERROR_422,
    },
)
def crear_vehiculo(entrada: VehiculoCrear) -> dict[str, object]:
    return servicio.crear_vehiculo(entrada)


@router.get(
    "", response_model=list[VehiculoRespuesta],
    summary="Listar vehiculos",
    description="Devuelve los vehiculos por ID ascendente, o una lista vacia. "
                "En esta etapa devuelve la lista completa; filtros, ordenamiento "
                "seleccionable y paginacion se incorporan en la Etapa 4.",
    responses={200: {"description": "Lista de vehiculos", "content": {
        "application/json": {"example": [EJEMPLO_VEHICULO]}}}},
)
def listar_vehiculos() -> list[dict[str, object]]:
    return servicio.listar_vehiculos()


@router.get(
    "/{id}", response_model=VehiculoRespuesta,
    summary="Consultar un vehiculo",
    description="Obtiene todos los datos del vehiculo identificado por un ID positivo.",
    responses={
        200: {"description": "Vehiculo encontrado", "content": {
            "application/json": {"example": EJEMPLO_VEHICULO}}},
        404: ERROR_404, 422: ERROR_422,
    },
)
def obtener_vehiculo(
    id: int = Path(gt=0, description="ID del vehiculo", examples=[1]),
) -> dict[str, object]:
    return servicio.obtener_vehiculo(id)


@router.patch(
    "/{id}", response_model=VehiculoRespuesta,
    summary="Actualizar un vehiculo parcialmente",
    description="Modifica solo los campos enviados. Rechaza ID, null y cuerpos vacios. "
                "La nueva sucursal debe existir. El unico cambio manual de estado "
                "permitido es disponible a vendido, sin reserva activa. "
                "Vendido es final; un error deja todos los campos sin cambios.",
    responses={
        200: {"description": "Vehiculo actualizado", "content": {
            "application/json": {"example": {**EJEMPLO_VEHICULO, "precio": 10500000}}}},
        400: {"model": ErrorRespuesta, "description": "Reservar o liberar manualmente no esta permitido",
              "content": {"application/json": {"example": {"error": {
                  "code": "STATE_MANAGED_BY_RESERVATIONS",
                  "message": "Solo se permite marcar vendido; reservas controla reservar y liberar",
                  "details": [],
              }}}}},
        404: ERROR_404,
        409: {"model": ErrorRespuesta, "description": "No esta disponible o tiene reserva activa",
              "content": {"application/json": {"example": {"error": {
                  "code": "STATE_CONFLICT",
                  "message": "Solo puede venderse un vehiculo disponible y sin reserva activa",
                  "details": [],
              }}}}},
        422: ERROR_422,
    },
)
def actualizar_vehiculo(
    id: int = Path(gt=0, description="ID del vehiculo", examples=[1]),
    entrada: VehiculoActualizar = Body(openapi_examples={
        "precio": {"summary": "Modificar solo el precio", "value": {"precio": 10500000}},
        "venta": {"summary": "Marcar vendido", "value": {"estado": "vendido"}},
    }),
) -> dict[str, object]:
    return servicio.actualizar_vehiculo(id, entrada)


@router.delete(
    "/{id}", status_code=204,
    summary="Eliminar un vehiculo sin historial",
    description="Elimina el vehiculo si ninguna reserva lo referencia, incluso cancelada "
                "o vencida. Devuelve 204 sin cuerpo y no reutiliza el ID eliminado.",
    responses={
        204: {"description": "Vehiculo eliminado; respuesta sin cuerpo"},
        404: ERROR_404,
        409: {"model": ErrorRespuesta, "description": "Existe historial de reservas",
              "content": {"application/json": {"example": {"error": {
                  "code": "RESERVATION_HISTORY_CONFLICT",
                  "message": "No se puede eliminar un vehiculo con historial de reservas",
                  "details": [],
              }}}}},
        422: ERROR_422,
    },
)
def eliminar_vehiculo(
    id: int = Path(gt=0, description="ID del vehiculo", examples=[1]),
) -> Response:
    servicio.eliminar_vehiculo(id)
    return Response(status_code=204)
