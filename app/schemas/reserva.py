"""Datos de entrada y salida del modulo de reservas (Pydantic v2)."""

from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.domain.reserva import EstadoReserva


class ReservaCrear(BaseModel):
    """El servidor asigna id, fecha_reserva y estado; se rechazan en la entrada."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "cliente_id": 1,
                "vehiculo_id": 3,
                "fecha_vencimiento": "2026-10-12",
                "monto_reserva": 500000,
            }
        },
    )

    cliente_id: int = Field(gt=0, strict=True, description="ID de un cliente existente")
    vehiculo_id: int = Field(gt=0, strict=True, description="ID de un vehiculo disponible")
    fecha_vencimiento: date = Field(
        description="Ultimo dia de la reserva (AAAA-MM-DD); no puede ser anterior a hoy"
    )
    monto_reserva: int = Field(gt=0, strict=True, description="Monto en pesos chilenos")


class ReservaActualizar(BaseModel):
    """PATCH solo acepta cancelar: {"estado": "cancelada"}."""

    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={"example": {"estado": "cancelada"}},
    )

    estado: Literal["cancelada"]


class ReservaRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    cliente_id: int
    vehiculo_id: int
    fecha_reserva: date
    fecha_vencimiento: date
    monto_reserva: int
    estado: EstadoReserva
