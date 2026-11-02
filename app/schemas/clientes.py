"""DTO del modulo de clientes."""

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ClienteCrear(BaseModel):
    """Datos necesarios para registrar un cliente."""

    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )

    rut: str = Field(min_length=3, max_length=20)
    nombre: str = Field(min_length=2, max_length=100)
    correo: EmailStr
    telefono: str = Field(min_length=1, max_length=30)
    direccion: str = Field(min_length=1, max_length=200)


class ClienteRespuesta(ClienteCrear):
    """Datos de un cliente devueltos por la API."""

    id: int = Field(gt=0, strict=True)
