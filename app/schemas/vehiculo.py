"""Datos de entrada y salida del modulo de vehiculos (Pydantic v2)."""

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.vehiculo import Condicion, EstadoVehiculo, Transmision


class VehiculoCrear(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        json_schema_extra={
            "example": {
                "marca": "Toyota",
                "modelo": "Yaris",
                "anio": 2022,
                "precio": 10990000,
                "kilometraje": 23000,
                "transmision": "manual",
                "condicion": "usado",
                "sucursal_id": 1,
            }
        },
    )

    marca: str = Field(min_length=2, max_length=50)
    modelo: str = Field(min_length=2, max_length=50)
    anio: int = Field(ge=1900, le=2100, strict=True)
    precio: int = Field(gt=0, strict=True)
    kilometraje: int = Field(ge=0, strict=True)
    transmision: Transmision
    condicion: Condicion
    sucursal_id: int = Field(gt=0, strict=True)


class VehiculoActualizar(BaseModel):
    model_config = ConfigDict(extra="forbid")

    marca: str | None = Field(default=None, min_length=2, max_length=50)
    modelo: str | None = Field(default=None, min_length=2, max_length=50)
    anio: int | None = Field(default=None, ge=1900, le=2100, strict=True)
    precio: int | None = Field(default=None, gt=0, strict=True)
    kilometraje: int | None = Field(default=None, ge=0, strict=True)
    transmision: Transmision | None = None
    condicion: Condicion | None = None
    estado: EstadoVehiculo | None = None
    sucursal_id: int | None = Field(default=None, gt=0, strict=True)

    @model_validator(mode="before")
    @classmethod
    def rechazar_vacios_y_nulos(cls, datos: Any) -> Any:
        if isinstance(datos, dict):
            if not datos:
                raise ValueError("Indica al menos un campo para actualizar")
            if any(valor is None for valor in datos.values()):
                raise ValueError("No se permiten valores nulos en PATCH")
        return datos


class VehiculoRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    marca: str
    modelo: str
    anio: int
    precio: int
    kilometraje: int
    transmision: Transmision
    condicion: Condicion
    estado: EstadoVehiculo
    sucursal_id: int


class VehiculosPaginados(BaseModel):
    items: list[VehiculoRespuesta]
    total: int
    pagina: int
    limite: int
    total_paginas: int
