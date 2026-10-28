"""Esquemas de validación para los clientes."""


from pydantic import BaseModel, ConfigDict, Field


class ClienteCrear(BaseModel):
    
    model_config = ConfigDict(extra="forbid")

    rut: str = Field(min_length=1, strict=True)
    nombre: str = Field(min_length=1, strict=True)
    correo: str = Field(min_length=1, strict=True)
    telefono: str = Field(min_length=1, strict=True)
    direccion: str = Field(min_length=1, strict=True)


class ClienteRespuesta(BaseModel):

    model_config = ConfigDict(extra="forbid")

    id: int = Field(gt=0, strict=True)
    rut: str
    nombre: str
    correo: str
    telefono: str
    direccion: str