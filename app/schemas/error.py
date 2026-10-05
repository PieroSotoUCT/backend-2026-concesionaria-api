"""DTO de errores para documentar las respuestas reales en Swagger."""

from pydantic import BaseModel, Field


class ContenidoError(BaseModel):
    code: str
    message: str
    details: list[dict[str, str]] = Field(default_factory=list)


class ErrorRespuesta(BaseModel):
    error: ContenidoError
