"""DTO del modulo de sucursales."""

from pydantic import BaseModel, ConfigDict, Field


class SucursalCrear(BaseModel):
    """Datos necesarios para registrar una sucursal."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    nombre: str = Field(min_length=2, max_length=100)
    direccion: str = Field(min_length=1, max_length=200)
    ciudad: str = Field(min_length=2, max_length=100)
    telefono: str = Field(min_length=1, max_length=30)
    horario_atencion: str = Field(min_length=1, max_length=120)


class SucursalRespuesta(SucursalCrear):
    """Datos de una sucursal devueltos por la API."""

    id: int = Field(gt=0, strict=True)
