"""Entidad y valores permitidos para vehiculos."""

from enum import Enum


class Transmision(str, Enum):
    MANUAL = "manual"
    AUTOMATICA = "automatica"


class Condicion(str, Enum):
    NUEVO = "nuevo"
    USADO = "usado"


class EstadoVehiculo(str, Enum):
    DISPONIBLE = "disponible"
    RESERVADO = "reservado"
    VENDIDO = "vendido"
