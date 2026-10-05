"""Pruebas repetibles del CRUD y las reglas propias de vehiculos.

Usan un servidor local con memoria independiente; no modifican una API abierta.
"""

import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.datos_demo import cargar_datos_demo
from app.errores import ErrorAplicacion
from app.repositories import datos
from app.repositories import vehiculos as repositorio
from app.schemas.vehiculo import VehiculoActualizar
from app.services import vehiculos as servicio


class PruebasVehiculosHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]
        cls.url = f"http://127.0.0.1:{puerto}"
        entorno = dict(os.environ, CONCESIONARIA_DATOS_DEMO="1")
        cls.proceso = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "app.main:app", "--host", "127.0.0.1",
             "--port", str(puerto)],
            cwd=Path(__file__).resolve().parents[1], env=entorno,
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
        )
        cls.addClassCleanup(cls.detener_servidor)
        for _ in range(100):
            try:
                with urlopen(cls.url + "/health", timeout=1) as respuesta:
                    if respuesta.status == 200:
                        return
            except (URLError, TimeoutError):
                if cls.proceso.poll() is not None:
                    raise RuntimeError("El servidor de pruebas termino antes de iniciar")
                time.sleep(0.1)
        raise RuntimeError("El servidor de pruebas no inicio a tiempo")

    @classmethod
    def detener_servidor(cls):
        cls.proceso.terminate()
        cls.proceso.wait(timeout=10)

    def solicitar(self, metodo, ruta, cuerpo=None):
        contenido = json.dumps(cuerpo).encode() if cuerpo is not None else None
        solicitud = Request(self.url + ruta, data=contenido, method=metodo,
                            headers={"Content-Type": "application/json"})
        try:
            respuesta = urlopen(solicitud, timeout=5)
        except HTTPError as error:
            respuesta = error
        with respuesta:
            cuerpo = respuesta.read()
            return respuesta.status, json.loads(cuerpo) if cuerpo else None

    def crear(self, **cambios):
        entrada = {
            "marca": "Toyota", "modelo": "Yaris", "anio": 2022, "precio": 10000000,
            "kilometraje": 10000, "transmision": "manual", "condicion": "usado",
            "sucursal_id": 1,
        }
        entrada.update(cambios)
        return self.solicitar("POST", "/vehiculos", entrada)

    def comprobar_error(self, respuesta, estado):
        codigo, cuerpo = respuesta
        self.assertEqual(codigo, estado)
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(set(cuerpo["error"]), {"code", "message", "details"})
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_crud_y_id_no_reutilizado(self):
        estado, creado = self.crear()
        self.assertEqual(estado, 201)
        self.assertEqual(creado["estado"], "disponible")
        ruta = f'/vehiculos/{creado["id"]}'
        self.assertEqual(self.solicitar("GET", ruta), (200, creado))
        estado, actualizado = self.solicitar("PATCH", ruta, {"precio": 9000000, "sucursal_id": 2})
        self.assertEqual(estado, 200)
        self.assertEqual(actualizado, {**creado, "precio": 9000000, "sucursal_id": 2})
        self.assertEqual(self.solicitar("DELETE", ruta), (204, None))
        self.comprobar_error(self.solicitar("GET", ruta), 404)
        estado, siguiente = self.crear()
        self.assertEqual(estado, 201)
        self.assertGreater(siguiente["id"], creado["id"])

    def test_datos_invalidos_al_crear(self):
        _, antes = self.solicitar("GET", "/vehiculos")
        for cambio in ({"id": 20}, {"estado": "vendido"}, {"precio": 0},
                       {"precio": 12.5}, {"kilometraje": -1}, {"marca": "A"},
                       {"anio": 1899}, {"transmision": "otra"}, {"sucursal_id": 0}):
            with self.subTest(cambio=cambio):
                self.comprobar_error(self.crear(**cambio), 422)
        self.assertEqual(self.solicitar("GET", "/vehiculos"), (200, antes))

    def test_sucursal_inexistente_y_patch_atomico(self):
        self.comprobar_error(self.crear(sucursal_id=999999), 404)
        _, creado = self.crear()
        ruta = f'/vehiculos/{creado["id"]}'
        self.comprobar_error(self.solicitar("PATCH", ruta, {"sucursal_id": 999999, "precio": 1}), 404)
        self.assertEqual(self.solicitar("GET", ruta), (200, creado))

    def test_patch_nulos_vacio_e_id(self):
        _, creado = self.crear()
        ruta = f'/vehiculos/{creado["id"]}'
        for cambio in ({}, {"precio": None}, {"marca": None}, {"estado": None}, {"id": 2},
                       {"precio": 12.5}, {"precio": -1}, {"marca": "A"}):
            with self.subTest(cambio=cambio):
                self.comprobar_error(self.solicitar("PATCH", ruta, cambio), 422)
        self.assertEqual(self.solicitar("GET", ruta), (200, creado))

    def test_eliminacion_con_historial(self):
        for id in (2, 3):
            with self.subTest(id=id):
                ruta = f"/vehiculos/{id}"
                antes = self.solicitar("GET", ruta)
                self.comprobar_error(self.solicitar("DELETE", ruta), 409)
                self.assertEqual(self.solicitar("GET", ruta), antes)

    def test_reserva_impide_liberar_y_vender(self):
        antes = self.solicitar("GET", "/vehiculos/3")
        self.comprobar_error(self.solicitar("PATCH", "/vehiculos/3", {"estado": "disponible"}), 400)
        self.comprobar_error(self.solicitar("PATCH", "/vehiculos/3", {"estado": "vendido", "precio": 1}), 409)
        self.assertEqual(self.solicitar("GET", "/vehiculos/3"), antes)

    def test_venta_y_estado_final(self):
        _, creado = self.crear()
        ruta = f'/vehiculos/{creado["id"]}'
        self.comprobar_error(self.solicitar("PATCH", ruta, {"estado": "reservado"}), 400)
        self.assertEqual(self.solicitar("PATCH", ruta, {"estado": "vendido"}),
                         (200, {**creado, "estado": "vendido"}))
        self.comprobar_error(self.solicitar("PATCH", ruta, {"estado": "disponible"}), 400)
        self.comprobar_error(self.solicitar("PATCH", ruta, {"estado": "vendido"}), 409)

    def test_ids_invalidos_e_inexistentes(self):
        for metodo in ("GET", "PATCH", "DELETE"):
            for id, esperado in (("0", 422), ("abc", 422), ("999999", 404)):
                with self.subTest(metodo=metodo, id=id):
                    cuerpo = {"precio": 1000} if metodo == "PATCH" else None
                    self.comprobar_error(self.solicitar(metodo, f"/vehiculos/{id}", cuerpo), esperado)

    def test_listado_y_openapi(self):
        estado, lista = self.solicitar("GET", "/vehiculos")
        self.assertEqual(estado, 200)
        self.assertEqual([v["id"] for v in lista], sorted(v["id"] for v in lista))
        estado, esquema = self.solicitar("GET", "/openapi.json")
        self.assertEqual(estado, 200)
        self.assertEqual(set(esquema["paths"]["/vehiculos"]), {"get", "post"})
        self.assertEqual(set(esquema["paths"]["/vehiculos/{id}"]), {"get", "patch", "delete"})
        referencia = esquema["paths"]["/vehiculos"]["post"]["responses"]["422"]["content"]["application/json"]["schema"]["$ref"]
        self.assertTrue(referencia.endswith("/ErrorRespuesta"))
        self.assertNotIn("content", esquema["paths"]["/vehiculos/{id}"]["delete"]["responses"]["204"])
        propiedades = esquema["components"]["schemas"]["VehiculoActualizar"]["properties"]
        for propiedad in propiedades.values():
            self.assertNotIn('"type": "null"', json.dumps(propiedad))


class PruebasReglasConDatosCompartidos(unittest.TestCase):
    def setUp(self):
        for coleccion in (datos.vehiculos, datos.sucursales, datos.clientes, datos.reservas):
            coleccion.clear()
        for nombre in datos.contadores:
            datos.contadores[nombre] = 0
        cargar_datos_demo()

    def test_reserva_activa_impide_venta_aunque_estado_sea_incoherente(self):
        datos.vehiculos[3]["estado"] = "disponible"
        antes = dict(datos.vehiculos[3])
        with self.assertRaises(ErrorAplicacion) as fallo:
            servicio.actualizar_vehiculo(3, VehiculoActualizar(estado="vendido", precio=1))
        self.assertEqual(fallo.exception.estado_http, 409)
        self.assertEqual(datos.vehiculos[3], antes)

    def test_historial_vencido_tambien_impide_eliminar(self):
        datos.reservas[1]["estado"] = "vencida"
        with self.assertRaises(ErrorAplicacion) as fallo:
            servicio.eliminar_vehiculo(2)
        self.assertEqual(fallo.exception.estado_http, 409)
        self.assertIn(2, datos.vehiculos)

    def test_consulta_no_expone_registro_mutable_y_lista_vacia(self):
        copia = repositorio.obtener(1)
        copia["precio"] = 1
        self.assertNotEqual(datos.vehiculos[1]["precio"], 1)
        datos.vehiculos.clear()
        self.assertEqual(servicio.listar_vehiculos(), [])
