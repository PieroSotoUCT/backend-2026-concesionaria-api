"""Operaciones del modulo de vehiculos respaldadas por ORM."""

from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.domain.vehiculo import EstadoVehiculo
from app.errores import ErrorAplicacion
from app.models import Vehiculo
from app.repositories import vehiculos as repositorio
from app.schemas.vehiculo import ConsultaVehiculos, VehiculoActualizar, VehiculoCrear
from app.services.reservas import procesar_vencimientos

def _registro(vehiculo: Vehiculo) -> dict[str, object]:
    return {campo: getattr(vehiculo, campo) for campo in (
        "id", "marca", "modelo", "anio", "precio", "kilometraje",
        "transmision", "condicion", "estado", "sucursal_id",
    )}


def comprobar_sucursal(session: Session, sucursal_id: int) -> None:
    if not repositorio.sucursal_existe(session, sucursal_id):
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La sucursal no existe")


def crear_vehiculo(entrada: VehiculoCrear) -> dict[str, object]:
    with SessionLocal.begin() as session:
        comprobar_sucursal(session, entrada.sucursal_id)
        vehiculo = Vehiculo(**entrada.model_dump(), estado=EstadoVehiculo.DISPONIBLE.value)
        repositorio.guardar(session, vehiculo)
        return _registro(vehiculo)


def listar_vehiculos(consulta: ConsultaVehiculos) -> dict[str, object]:
    procesar_vencimientos()
    with SessionLocal() as session:
        encontrados, total = repositorio.consultar(
            session, marca=consulta.marca,
            estado=consulta.estado.value if consulta.estado is not None else None,
            sucursal_id=consulta.sucursal_id, precio_min=consulta.precio_min,
            precio_max=consulta.precio_max, ordenar_por=consulta.ordenar_por,
            direccion=consulta.direccion, pagina=consulta.pagina, limite=consulta.limite,
        )
        return {
            "items": [_registro(v) for v in encontrados],
            "total": total, "pagina": consulta.pagina, "limite": consulta.limite,
            "total_paginas": (total + consulta.limite - 1) // consulta.limite,
        }


def obtener_vehiculo(id: int) -> dict[str, object]:
    procesar_vencimientos()
    with SessionLocal() as session:
        vehiculo = repositorio.obtener(session, id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        return _registro(vehiculo)


def actualizar_vehiculo(id: int, entrada: VehiculoActualizar) -> dict[str, object]:
    procesar_vencimientos()
    with SessionLocal.begin() as session:
        vehiculo = repositorio.obtener(session, id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        cambios = entrada.model_dump(mode="json", exclude_unset=True)
        comprobar_sucursal(session, cambios.get("sucursal_id", vehiculo.sucursal_id))
        if "estado" in cambios:
            if cambios["estado"] != "vendido":
                raise ErrorAplicacion(400, "STATE_MANAGED_BY_RESERVATIONS",
                                      "Solo se permite marcar vendido; reservas controla reservar y liberar")
            if vehiculo.estado != "disponible" or repositorio.tiene_reserva_activa(session, id):
                raise ErrorAplicacion(409, "STATE_CONFLICT",
                                      "Solo puede venderse un vehiculo disponible y sin reserva activa")
        for campo, valor in cambios.items():
            setattr(vehiculo, campo, valor.value if hasattr(valor, "value") else valor)
        repositorio.guardar(session, vehiculo)
        return _registro(vehiculo)


def eliminar_vehiculo(id: int) -> None:
    procesar_vencimientos()
    with SessionLocal.begin() as session:
        vehiculo = repositorio.obtener(session, id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        if repositorio.tiene_historial_reservas(session, id):
            raise ErrorAplicacion(409, "RESERVATION_HISTORY_CONFLICT",
                                  "No se puede eliminar un vehiculo con historial de reservas")
        repositorio.eliminar(session, vehiculo)
