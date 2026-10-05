"""Contrato HTTP de reservas; las reglas se delegan al servicio."""

from fastapi import APIRouter, Body, Path

from app.schemas.error import ErrorRespuesta
from app.schemas.reserva import ReservaActualizar, ReservaCrear, ReservaRespuesta
from app.services import reservas as servicio

router = APIRouter(prefix="/reservas", tags=["Reservas"])

EJEMPLO_RESERVA = {
    "id": 1, "cliente_id": 1, "vehiculo_id": 3,
    "fecha_reserva": "2026-10-05", "fecha_vencimiento": "2026-10-12",
    "monto_reserva": 500000, "estado": "activa",
}


def _error(descripcion: str, codigo: str, mensaje: str, detalles: list | None = None) -> dict:
    return {
        "model": ErrorRespuesta,
        "description": descripcion,
        "content": {"application/json": {"example": {"error": {
            "code": codigo, "message": mensaje, "details": detalles or [],
        }}}},
    }


ERROR_404 = _error("La reserva, el cliente o el vehiculo no existe",
                   "RESOURCE_NOT_FOUND", "La reserva no existe")
ERROR_422 = _error("Datos, campos adicionales o ID invalidos", "VALIDATION_ERROR",
                   "Datos o parametros invalidos",
                   [{"campo": "body.monto_reserva", "mensaje": "Input should be greater than 0"}])


@router.post(
    "", status_code=201, response_model=ReservaRespuesta,
    summary="Reservar un vehiculo",
    description="Crea una reserva activa para un cliente y un vehiculo existentes. "
                "El vehiculo debe estar disponible y pasa a reservado. El servidor asigna "
                "id, fecha_reserva (hoy) y estado; se rechazan en la entrada. "
                "fecha_vencimiento no puede ser anterior a hoy.",
    responses={
        201: {"description": "Reserva creada", "content": {
            "application/json": {"example": EJEMPLO_RESERVA}}},
        400: _error("La fecha de vencimiento es anterior a hoy",
                    "INVALID_EXPIRATION_DATE",
                    "La fecha de vencimiento no puede ser anterior a hoy"),
        404: ERROR_404,
        409: _error("El vehiculo esta reservado o vendido", "VEHICLE_NOT_AVAILABLE",
                    "Solo se puede reservar un vehiculo disponible"),
        422: ERROR_422,
    },
)
def crear_reserva(entrada: ReservaCrear) -> dict[str, object]:
    return servicio.crear_reserva(entrada)


@router.get(
    "", response_model=list[ReservaRespuesta],
    summary="Listar reservas",
    description="Devuelve todas las reservas, incluidas canceladas y vencidas, por ID "
                "ascendente. Antes de responder se procesan los vencimientos.",
    responses={200: {"description": "Lista de reservas (vacia si no hay ninguna)",
                     "content": {"application/json": {"example": [EJEMPLO_RESERVA]}}}},
)
def listar_reservas() -> list[dict[str, object]]:
    return servicio.listar_reservas()


@router.get(
    "/{id}", response_model=ReservaRespuesta,
    summary="Consultar una reserva",
    description="Obtiene la reserva identificada por un ID positivo, con su estado "
                "actualizado tras procesar vencimientos.",
    responses={
        200: {"description": "Reserva encontrada", "content": {
            "application/json": {"example": EJEMPLO_RESERVA}}},
        404: ERROR_404, 422: ERROR_422,
    },
)
def obtener_reserva(
    id: int = Path(gt=0, description="ID de la reserva", examples=[1]),
) -> dict[str, object]:
    return servicio.obtener_reserva(id)


@router.patch(
    "/{id}", response_model=ReservaRespuesta,
    summary="Cancelar una reserva",
    description="Solo acepta {\"estado\": \"cancelada\"}. Cancela una reserva activa y "
                "devuelve su vehiculo a disponible. Una reserva ya cancelada o vencida "
                "no puede cancelarse.",
    responses={
        200: {"description": "Reserva cancelada", "content": {
            "application/json": {"example": {**EJEMPLO_RESERVA, "estado": "cancelada"}}}},
        404: ERROR_404,
        409: _error("La reserva no esta activa", "STATE_CONFLICT",
                    "Solo se puede cancelar una reserva activa; esta cancelada"),
        422: ERROR_422,
    },
)
def cancelar_reserva(
    id: int = Path(gt=0, description="ID de la reserva", examples=[1]),
    entrada: ReservaActualizar = Body(openapi_examples={
        "cancelar": {"summary": "Cancelar la reserva", "value": {"estado": "cancelada"}},
    }),
) -> dict[str, object]:
    # El DTO solo admite "cancelada"; cualquier otro estado ya fallo con 422.
    return servicio.cancelar_reserva(id)
