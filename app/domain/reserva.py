"""Entidad y estados permitidos para reservas."""

from datetime import date
from enum import Enum


class EstadoReserva(str, Enum):
    ACTIVA = "activa"
    CANCELADA = "cancelada"
    VENCIDA = "vencida"


class Reserva:
    def __init__(
        self,
        id: int,
        cliente_id: int,
        vehiculo_id: int,
        fecha_reserva: date,
        fecha_vencimiento: date,
        monto_reserva: int,
        estado: EstadoReserva,
    ) -> None:
        self.id = id
        self.cliente_id = cliente_id
        self.vehiculo_id = vehiculo_id
        self.fecha_reserva = fecha_reserva
        self.fecha_vencimiento = fecha_vencimiento
        self.monto_reserva = monto_reserva
        self.estado = estado

    def a_registro(self) -> dict[str, object]:
        """Convierte la entidad al formato del almacenamiento comun."""
        return {
            "id": self.id,
            "cliente_id": self.cliente_id,
            "vehiculo_id": self.vehiculo_id,
            "fecha_reserva": self.fecha_reserva,
            "fecha_vencimiento": self.fecha_vencimiento,
            "monto_reserva": self.monto_reserva,
            "estado": self.estado.value,
        }
