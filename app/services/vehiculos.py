"""Operaciones del modulo de vehiculos respaldadas por ORM."""

from sqlalchemy import select

from app.db import SessionLocal, initialize_database
from app.domain.vehiculo import EstadoVehiculo
from app.errores import ErrorAplicacion
from app.models import Vehiculo
from app.repositories import vehiculos as repositorio
from app.schemas.vehiculo import ConsultaVehiculos, VehiculoActualizar, VehiculoCrear

initialize_database()


def _registro(vehiculo: Vehiculo) -> dict[str, object]:
    return {campo: getattr(vehiculo, campo) for campo in (
        "id", "marca", "modelo", "anio", "precio", "kilometraje",
        "transmision", "condicion", "estado", "sucursal_id",
    )}


def comprobar_sucursal(session, sucursal_id: int) -> None:
    if not repositorio.sucursal_existe(session, sucursal_id):
        raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "La sucursal no existe")


def crear_vehiculo(entrada: VehiculoCrear) -> dict[str, object]:
    with SessionLocal.begin() as session:
        comprobar_sucursal(session, entrada.sucursal_id)
        vehiculo = Vehiculo(**entrada.model_dump(), estado=EstadoVehiculo.DISPONIBLE.value)
        session.add(vehiculo)
        session.flush()
        return _registro(vehiculo)


def listar_vehiculos(consulta: ConsultaVehiculos) -> dict[str, object]:
    with SessionLocal() as session:
        query = select(Vehiculo)
        if consulta.marca is not None:
            query = query.where(Vehiculo.marca.ilike(consulta.marca))
        if consulta.estado is not None:
            query = query.where(Vehiculo.estado == consulta.estado.value)
        if consulta.sucursal_id is not None:
            query = query.where(Vehiculo.sucursal_id == consulta.sucursal_id)
        if consulta.precio_min is not None:
            query = query.where(Vehiculo.precio >= consulta.precio_min)
        if consulta.precio_max is not None:
            query = query.where(Vehiculo.precio <= consulta.precio_max)
        campo = getattr(Vehiculo, consulta.ordenar_por) if consulta.ordenar_por else Vehiculo.id
        query = query.order_by(campo.desc() if consulta.direccion == "desc" else campo,
                               Vehiculo.id)
        encontrados = list(session.scalars(query))
        total = len(encontrados)
        inicio = (consulta.pagina - 1) * consulta.limite
        return {
            "items": [_registro(v) for v in encontrados[inicio:inicio + consulta.limite]],
            "total": total, "pagina": consulta.pagina, "limite": consulta.limite,
            "total_paginas": (total + consulta.limite - 1) // consulta.limite,
        }


def obtener_vehiculo(id: int) -> dict[str, object]:
    with SessionLocal() as session:
        vehiculo = repositorio.obtener(session, id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        return _registro(vehiculo)


def actualizar_vehiculo(id: int, entrada: VehiculoActualizar) -> dict[str, object]:
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
        session.flush()
        return _registro(vehiculo)


def eliminar_vehiculo(id: int) -> None:
    with SessionLocal.begin() as session:
        vehiculo = repositorio.obtener(session, id)
        if vehiculo is None:
            raise ErrorAplicacion(404, "RESOURCE_NOT_FOUND", "El vehiculo no existe")
        if repositorio.tiene_historial_reservas(session, id):
            raise ErrorAplicacion(409, "RESERVATION_HISTORY_CONFLICT",
                                  "No se puede eliminar un vehiculo con historial de reservas")
        repositorio.eliminar(session, vehiculo)
