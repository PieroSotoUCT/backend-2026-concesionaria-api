"""DTO del modulo de clientes."""

from pydantic import BaseModel, ConfigDict, Field


class ClienteCrear(BaseModel):
    model_config = ConfigDict(extra="forbid")

    rut: str = Field(min_length=3, max_length=20)
    nombre: str = Field(min_length=2, max_length=100)
    correo: str = Field(min_length=3, max_length=254)
    telefono: str = Field(min_length=1, max_length=30)
    direccion: str = Field(min_length=1, max_length=200)


class ClienteRespuesta(ClienteCrear):
    id: int

