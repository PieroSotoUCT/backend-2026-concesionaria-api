"""Pruebas del modulo de reservas.

Servicio: se ejecuta en el mismo proceso sobre las colecciones compartidas.
HTTP: un servidor Uvicorn propio y con memoria independiente, sembrado con
clientes, vehiculos y una reserva vencida (el modulo de vehiculos aun no esta en main).
"""

import json
import os
import socket
import subprocess
import sys
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.errores import ErrorAplicacion
from app.repositories import datos
from app.schemas.reserva import ReservaCrear
from app.services import reservas as servicio

SEMBRADO = """
from datetime import date, timedelta
import uvicorn
from app.repositories import datos
from app.main import app

for _ in range(2):
    i = datos.siguiente_id("clientes")
    datos.clientes[i] = {"id": i, "rut": f"1-{i}", "nombre": f"Cliente {i}",
                         "correo": "c@example.com", "telefono": "1", "direccion": "x"}
for estado in ("disponible", "disponible", "reservado", "vendido"):
    i = datos.siguiente_id("vehiculos")
    datos.vehiculos[i] = {"id": i, "marca": "Toyota", "modelo": "Yaris", "anio": 2022,
                          "precio": 10000000, "kilometraje": 1, "transmision": "manual",
                          "condicion": "usado", "estado": estado, "sucursal_id": 1}
i = datos.siguiente_id("reservas")
datos.reservas[i] = {"id": i, "cliente_id": 1, "vehiculo_id": 3,
                     "fecha_reserva": date.today() - timedelta(days=10),
                     "fecha_vencimiento": date.today() - timedelta(days=1),
                     "monto_reserva": 100000, "estado": "activa"}
uvicorn.run(app, host="127.0.0.1", port=int(__import__("sys").argv[1]), log_level="warning")
"""


def reiniciar_datos():
    for coleccion in (datos.vehiculos, datos.sucursales, datos.clientes, datos.reservas):
        coleccion.clear()
    for nombre in datos.contadores:
        datos.contadores[nombre] = 0


def sembrar_servicio():
    reiniciar_datos()
    datos.clientes[datos.siguiente_id("clientes")] = {"id": 1, "rut": "1-9", "nombre": "Ana"}
    for estado in ("disponible", "disponible", "vendido"):
        i = datos.siguiente_id("vehiculos")
        datos.vehiculos[i] = {"id": i, "estado": estado}


def entrada(**cambios):
    base = {"cliente_id": 1, "vehiculo_id": 1,
            "fecha_vencimiento": date.today() + timedelta(days=7), "monto_reserva": 500000}
    return ReservaCrear(**{**base, **cambios})


class PruebasServicioReservas(unittest.TestCase):
    def setUp(self):
        sembrar_servicio()

    def tearDown(self):
        reiniciar_datos()

    def test_crear_reserva_marca_vehiculo_reservado(self):
        reserva = servicio.crear_reserva(entrada())
        self.assertEqual(reserva["estado"], "activa")
        self.assertEqual(reserva["fecha_reserva"], date.today())
        self.assertEqual(datos.vehiculos[1]["estado"], "reservado")

    def test_reservar_hoy_es_valido(self):
        reserva = servicio.crear_reserva(entrada(fecha_vencimiento=date.today()))
        self.assertEqual(reserva["estado"], "activa")

    def test_cliente_o_vehiculo_inexistente_da_404_sin_efectos(self):
        for cambios in ({"cliente_id": 99}, {"vehiculo_id": 99}):
            with self.assertRaises(ErrorAplicacion) as contexto:
                servicio.crear_reserva(entrada(**cambios))
            self.assertEqual(contexto.exception.estado_http, 404)
        self.assertEqual(datos.reservas, {})
        self.assertEqual(datos.contadores["reservas"], 0)

    def test_fecha_anterior_a_hoy_da_400(self):
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.crear_reserva(entrada(fecha_vencimiento=date.today() - timedelta(days=1)))
        self.assertEqual(contexto.exception.estado_http, 400)
        self.assertEqual(datos.vehiculos[1]["estado"], "disponible")

    def test_vehiculo_reservado_o_vendido_da_409(self):
        servicio.crear_reserva(entrada())
        for vehiculo_id in (1, 3):
            with self.assertRaises(ErrorAplicacion) as contexto:
                servicio.crear_reserva(entrada(vehiculo_id=vehiculo_id))
            self.assertEqual(contexto.exception.estado_http, 409)
            self.assertEqual(contexto.exception.codigo, "VEHICLE_NOT_AVAILABLE")
        self.assertEqual(len(datos.reservas), 1)

    def test_cancelar_libera_vehiculo(self):
        servicio.crear_reserva(entrada())
        reserva = servicio.cancelar_reserva(1)
        self.assertEqual(reserva["estado"], "cancelada")
        self.assertEqual(datos.vehiculos[1]["estado"], "disponible")

    def test_cancelar_dos_veces_da_409_y_no_existente_404(self):
        servicio.crear_reserva(entrada())
        servicio.cancelar_reserva(1)
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(1)
        self.assertEqual(contexto.exception.estado_http, 409)
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(99)
        self.assertEqual(contexto.exception.estado_http, 404)

    def test_vencimiento_libera_vehiculo_y_es_idempotente(self):
        servicio.crear_reserva(entrada(fecha_vencimiento=date.today() + timedelta(days=2)))
        self.assertEqual(servicio.procesar_vencimientos(date.today() + timedelta(days=2)), 0)
        self.assertEqual(datos.reservas[1]["estado"], "activa")
        manana_del_limite = date.today() + timedelta(days=3)
        self.assertEqual(servicio.procesar_vencimientos(manana_del_limite), 1)
        self.assertEqual(datos.reservas[1]["estado"], "vencida")
        self.assertEqual(datos.vehiculos[1]["estado"], "disponible")
        self.assertEqual(servicio.procesar_vencimientos(manana_del_limite), 0)

    def test_vencimiento_no_toca_canceladas_ni_vehiculos_vendidos(self):
        servicio.crear_reserva(entrada())
        servicio.cancelar_reserva(1)
        datos.vehiculos[1]["estado"] = "vendido"
        servicio.procesar_vencimientos(date.today() + timedelta(days=30))
        self.assertEqual(datos.reservas[1]["estado"], "cancelada")
        self.assertEqual(datos.vehiculos[1]["estado"], "vendido")

    def test_vencida_no_se_puede_cancelar(self):
        servicio.crear_reserva(entrada())
        datos.reservas[1]["fecha_vencimiento"] = date.today() - timedelta(days=1)
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(1)
        self.assertEqual(contexto.exception.estado_http, 409)
        self.assertEqual(datos.reservas[1]["estado"], "vencida")
        self.assertEqual(datos.vehiculos[1]["estado"], "disponible")

    def test_listar_ordena_por_id_y_procesa_vencimientos(self):
        servicio.crear_reserva(entrada())
        servicio.crear_reserva(entrada(vehiculo_id=2))
        datos.reservas[1]["fecha_vencimiento"] = date.today() - timedelta(days=1)
        lista = servicio.listar_reservas()
        self.assertEqual([r["id"] for r in lista], [1, 2])
        self.assertEqual([r["estado"] for r in lista], ["vencida", "activa"])

    def test_vehiculo_liberado_puede_reservarse_de_nuevo(self):
        servicio.crear_reserva(entrada())
        servicio.cancelar_reserva(1)
        nueva = servicio.crear_reserva(entrada())
        self.assertEqual(nueva["id"], 2)
        self.assertEqual(datos.vehiculos[1]["estado"], "reservado")


class PruebasReservasHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]
        cls.url = f"http://127.0.0.1:{puerto}"
        cls.proceso = subprocess.Popen(
            [sys.executable, "-c", SEMBRADO, str(puerto)],
            cwd=Path(__file__).resolve().parents[1],
            stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT,
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

    def cuerpo(self, **cambios):
        base = {"cliente_id": 1, "vehiculo_id": 1,
                "fecha_vencimiento": (date.today() + timedelta(days=5)).isoformat(),
                "monto_reserva": 450000}
        return {**base, **cambios}

    def assertError(self, resultado, estado, codigo):
        status, cuerpo = resultado
        self.assertEqual(status, estado)
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(cuerpo["error"]["code"], codigo)
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_flujo_completo_y_formato_de_errores(self):
        # La reserva sembrada vencio ayer: aparece como vencida.
        status, vencida = self.solicitar("GET", "/reservas/1")
        self.assertEqual((status, vencida["estado"]), (200, "vencida"))

        status, creada = self.solicitar("POST", "/reservas", self.cuerpo())
        self.assertEqual(status, 201)
        self.assertEqual(creada["estado"], "activa")
        self.assertEqual(creada["fecha_reserva"], date.today().isoformat())
        self.assertEqual(self.solicitar("GET", f"/reservas/{creada['id']}")[1], creada)

        # El mismo vehiculo ya no esta disponible.
        self.assertError(self.solicitar("POST", "/reservas", self.cuerpo()),
                         409, "VEHICLE_NOT_AVAILABLE")

        status, lista = self.solicitar("GET", "/reservas")
        self.assertEqual(status, 200)
        self.assertEqual([r["id"] for r in lista], sorted(r["id"] for r in lista))

        status, cancelada = self.solicitar("PATCH", f"/reservas/{creada['id']}",
                                           {"estado": "cancelada"})
        self.assertEqual((status, cancelada["estado"]), (200, "cancelada"))
        self.assertError(self.solicitar("PATCH", f"/reservas/{creada['id']}",
                                        {"estado": "cancelada"}), 409, "STATE_CONFLICT")
        # Liberado: puede reservarse otra vez.
        self.assertEqual(self.solicitar("POST", "/reservas", self.cuerpo())[0], 201)

    def test_errores_de_negocio(self):
        self.assertError(self.solicitar("POST", "/reservas", self.cuerpo(cliente_id=99)),
                         404, "RESOURCE_NOT_FOUND")
        self.assertError(self.solicitar("POST", "/reservas", self.cuerpo(vehiculo_id=99)),
                         404, "RESOURCE_NOT_FOUND")
        ayer = (date.today() - timedelta(days=1)).isoformat()
        self.assertError(self.solicitar("POST", "/reservas",
                                        self.cuerpo(vehiculo_id=2, fecha_vencimiento=ayer)),
                         400, "INVALID_EXPIRATION_DATE")
        for vehiculo_id in (4,):  # vendido
            self.assertError(self.solicitar("POST", "/reservas",
                                            self.cuerpo(vehiculo_id=vehiculo_id)),
                             409, "VEHICLE_NOT_AVAILABLE")
        self.assertError(self.solicitar("GET", "/reservas/999"), 404, "RESOURCE_NOT_FOUND")
        self.assertError(self.solicitar("PATCH", "/reservas/999", {"estado": "cancelada"}),
                         404, "RESOURCE_NOT_FOUND")

    def test_validaciones_422(self):
        casos = [
            self.cuerpo(monto_reserva=0), self.cuerpo(monto_reserva="500"),
            self.cuerpo(cliente_id=0), self.cuerpo(vehiculo_id="1"),
            self.cuerpo(fecha_vencimiento="manana"), self.cuerpo(id=7),
            self.cuerpo(estado="activa"), self.cuerpo(fecha_reserva="2026-01-01"),
        ]
        sin_campo = self.cuerpo()
        del sin_campo["monto_reserva"]
        casos.append(sin_campo)
        for caso in casos:
            self.assertError(self.solicitar("POST", "/reservas", caso), 422, "VALIDATION_ERROR")
        for ruta in ("/reservas/0", "/reservas/abc"):
            self.assertError(self.solicitar("GET", ruta), 422, "VALIDATION_ERROR")
        for cuerpo in ({"estado": "activa"}, {"estado": "vencida"}, {"estado": None}, {},
                       {"estado": "cancelada", "monto_reserva": 1}):
            self.assertError(self.solicitar("PATCH", "/reservas/1", cuerpo),
                             422, "VALIDATION_ERROR")


if __name__ == "__main__":
    unittest.main()
