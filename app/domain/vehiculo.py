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


class Vehiculo:
    def __init__(
        self,
        id: int,
        marca: str,
        modelo: str,
        anio: int,
        precio: int,
        kilometraje: int,
        transmision: Transmision,
        condicion: Condicion,
        estado: EstadoVehiculo,
        sucursal_id: int,
    ) -> None:
        self.id = id
        self.marca = marca
        self.modelo = modelo
        self.anio = anio
        self.precio = precio
        self.kilometraje = kilometraje
        self.transmision = transmision
        self.condicion = condicion
        self.estado = estado
        self.sucursal_id = sucursal_id

    def a_registro(self) -> dict[str, object]:
        """Convierte la entidad al formato del almacenamiento comun."""
        return {
            "id": self.id,
            "marca": self.marca,
            "modelo": self.modelo,
            "anio": self.anio,
            "precio": self.precio,
            "kilometraje": self.kilometraje,
            "transmision": self.transmision.value,
            "condicion": self.condicion.value,
            "estado": self.estado.value,
            "sucursal_id": self.sucursal_id,
        }
