"""Flujo HTTP de vehiculos sobre una SQLite temporal migrada."""

import json
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from tests.soporte_bd import entorno_base_temporal


RAIZ = Path(__file__).resolve().parents[1]


def solicitar(
    url: str, metodo: str, ruta: str, datos: dict[str, Any] | None = None,
) -> tuple[int, object | None]:
    cuerpo = json.dumps(datos).encode() if datos is not None else None
    peticion = Request(url + ruta, data=cuerpo, method=metodo,
                       headers={"Content-Type": "application/json"})
    try:
        respuesta = urlopen(peticion, timeout=5)
    except HTTPError as error:
        respuesta = error
    with respuesta:
        estado = respuesta.status
        if not isinstance(estado, int):
            raise AssertionError(f"Estado HTTP invalido en {metodo} {ruta}")
        contenido = respuesta.read()
        return estado, json.loads(contenido) if contenido else None


def solicitar_json(
    url: str, metodo: str, ruta: str, datos: dict[str, Any] | None = None,
) -> tuple[int, dict[str, Any]]:
    estado, cuerpo = solicitar(url, metodo, ruta, datos)
    if not isinstance(cuerpo, dict):
        raise AssertionError(f"Se esperaba una respuesta JSON en {metodo} {ruta}")
    return estado, cast(dict[str, Any], cuerpo)


class PruebasVehiculosORM(unittest.TestCase):
    def test_crud_consulta_reglas_y_vencimiento(self):
        with entorno_base_temporal() as (entorno, _ruta):
            subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"],
                           cwd=RAIZ, env=entorno, check=True, capture_output=True, text=True)
            sembrado = """
import json
from datetime import date, timedelta
from app.db import SessionLocal
from app.models import Cliente, Reserva, Sucursal, Vehiculo
with SessionLocal.begin() as session:
    a = Sucursal(nombre='Centro', direccion='A', ciudad='Temuco',
                 telefono='1', horario_atencion='9-18')
    b = Sucursal(nombre='Sur', direccion='B', ciudad='Valdivia',
                 telefono='2', horario_atencion='9-18')
    cliente = Cliente(rut='12345678-9', nombre='Ana', correo='ana@example.com',
                      telefono='3', direccion='C')
    session.add_all([a, b, cliente])
    session.flush()
    vehiculos = []
    for modelo, precio, estado, sucursal in (
        ('A1', 100, 'disponible', a), ('B2', 300, 'reservado', b),
        ('C3', 300, 'reservado', b), ('D4', 500, 'disponible', b),
    ):
        vehiculo = Vehiculo(marca='Prueba', modelo=modelo, anio=2022,
            precio=precio, kilometraje=0, transmision='manual',
            condicion='usado', estado=estado, sucursal=sucursal)
        session.add(vehiculo)
        vehiculos.append(vehiculo)
    session.flush()
    for vehiculo, estado, fecha in (
        (vehiculos[1], 'activa', date.today() + timedelta(days=1)),
        (vehiculos[2], 'activa', date.today() - timedelta(days=1)),
        (vehiculos[3], 'cancelada', date.today() - timedelta(days=1)),
    ):
        session.add(Reserva(cliente=cliente, vehiculo=vehiculo,
            fecha_reserva=date.today() - timedelta(days=2),
            fecha_vencimiento=fecha, monto_reserva=10, estado=estado))
    print(json.dumps({'sucursales': [a.id, b.id],
                      'vehiculos': [v.id for v in vehiculos]}))
"""
            salida = subprocess.run([sys.executable, "-c", sembrado],
                                    cwd=RAIZ, env=entorno, check=True,
                                    capture_output=True, text=True)
            ids = json.loads(salida.stdout)
            centro, sur = ids["sucursales"]
            libre, reservado, vencido, historial = ids["vehiculos"]
            with socket.socket() as conexion:
                conexion.bind(("127.0.0.1", 0))
                puerto = conexion.getsockname()[1]
            url = f"http://127.0.0.1:{puerto}"
            proceso = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host",
                 "127.0.0.1", "--port", str(puerto)], cwd=RAIZ, env=entorno,
                stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            try:
                for _ in range(100):
                    try:
                        if solicitar(url, "GET", "/health")[0] == 200:
                            break
                    except (URLError, TimeoutError):
                        if proceso.poll() is not None:
                            self.fail("El servidor termino antes de responder")
                        time.sleep(0.1)
                else:
                    self.fail("El servidor no inicio a tiempo")

                self.assertEqual(solicitar_json(url, "GET", f"/vehiculos/{vencido}")[1]["estado"],
                                 "disponible")
                parametros = urlencode({"marca": "  pRuEbA  ", "estado": "disponible",
                    "sucursal_id": sur, "precio_min": 300, "precio_max": 500,
                    "ordenar_por": "precio", "direccion": "desc", "pagina": 1,
                    "limite": 2})
                estado, lista = solicitar_json(url, "GET", "/vehiculos?" + parametros)
                self.assertEqual(estado, 200)
                self.assertEqual([v["id"] for v in lista["items"]], [historial, vencido])
                self.assertEqual(lista["total"], 2)
                pagina_dos = urlencode({"marca": "Prueba", "estado": "disponible",
                    "sucursal_id": sur, "precio_min": 300, "precio_max": 500,
                    "ordenar_por": "precio", "direccion": "desc", "pagina": 2,
                    "limite": 1})
                _, segunda = solicitar_json(url, "GET", "/vehiculos?" + pagina_dos)
                self.assertEqual([v["id"] for v in segunda["items"]], [vencido])
                self.assertEqual((segunda["total"], segunda["total_paginas"]), (2, 2))
                self.assertEqual(solicitar(url, "PATCH", f"/vehiculos/{libre}",
                    {"estado": "vendido"})[0], 200)
                self.assertEqual(solicitar(url, "PATCH", f"/vehiculos/{libre}",
                    {"estado": "disponible"})[0], 400)

                nuevo = {"marca": "Toyota", "modelo": "Yaris", "anio": 2022,
                    "precio": 10000000, "kilometraje": 10, "transmision": "manual",
                    "condicion": "usado", "sucursal_id": centro}
                self.assertEqual(solicitar(url, "POST", "/vehiculos", {**nuevo,
                    "sucursal_id": 99999})[0], 404)
                estado, creado = solicitar_json(url, "POST", "/vehiculos", nuevo)
                self.assertEqual(estado, 201)
                ruta = f'/vehiculos/{creado["id"]}'
                self.assertEqual(solicitar(url, "GET", ruta), (200, creado))
                self.assertEqual(solicitar_json(url, "PATCH", ruta, {"precio": 9000000})[1],
                                 {**creado, "precio": 9000000})
                error = solicitar_json(url, "PATCH", ruta,
                                  {"precio": 1, "sucursal_id": 99999})
                self.assertEqual(error[0], 404)
                self.assertEqual(set(error[1]["error"]), {"code", "message", "details"})
                self.assertEqual(solicitar_json(url, "GET", ruta)[1]["precio"], 9000000)
                self.assertEqual(solicitar(url, "PATCH", f"/vehiculos/{reservado}",
                    {"estado": "vendido", "precio": 1})[0], 409)
                self.assertEqual(solicitar_json(url, "GET", f"/vehiculos/{reservado}")[1]["precio"],
                                 300)
                self.assertEqual(solicitar(url, "DELETE", f"/vehiculos/{historial}")[0], 409)
                self.assertEqual(solicitar(url, "PATCH", ruta, {"estado": "vendido"})[0], 200)
                self.assertEqual(solicitar(url, "DELETE", ruta), (204, None))
                self.assertEqual(solicitar(url, "GET", ruta)[0], 404)
                self.assertEqual(solicitar(url, "POST", "/vehiculos",
                    {**nuevo, "precio": -1})[0], 422)
            finally:
                proceso.terminate()
                proceso.wait(timeout=10)
