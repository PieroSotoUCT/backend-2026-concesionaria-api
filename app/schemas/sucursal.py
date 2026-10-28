"""Esquemas de validación para las sucursales."""

from pydantic import BaseModel, ConfigDict, Field


class SucursalCrear(BaseModel):
    """Datos necesarios para registrar una sucursal."""

    model_config = ConfigDict(extra="forbid")

    nombre: str = Field(min_length=1, strict=True)
    direccion: str = Field(min_length=1, strict=True)
    ciudad: str = Field(min_length=1, strict=True)
    telefono: str = Field(min_length=1, strict=True)
    horario_atencion: str = Field(min_length=1, strict=True)


class SucursalRespuesta(BaseModel):
    """Estructura de respuesta de una sucursal."""

    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0, strict=True)
    nombre: str
    direccion: str
    ciudad: str
    telefono: str
    horario_atencion: str
