
"""Pruebas del módulo de clientes."""

import unittest
import json
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.errores import ErrorAplicacion
from app.repositories import datos
from app.services import clientes as servicio


def reiniciar_datos() -> None:
    """Limpia las colecciones compartidas antes de cada prueba."""
    for nombre in ("vehiculos", "sucursales", "clientes", "reservas"):
        getattr(datos, nombre).clear()

    for nombre in datos.contadores:
        datos.contadores[nombre] = 0


class PruebasServicioClientes(unittest.TestCase):
    def setUp(self) -> None:
        reiniciar_datos()

    def tearDown(self) -> None:
        reiniciar_datos()

    def datos_cliente(self, **cambios: str) -> dict[str, str]:
        """Construye los datos de un cliente para las pruebas."""
        base = {
            "rut": "12.345.678-k",
            "nombre": "Gabriel",
            "correo": "gabriel@example.com",
            "telefono": "912345678",
            "direccion": "Temuco",
        }
        return {**base, **cambios}

    def test_crear_cliente_normaliza_rut_y_asigna_id(self) -> None:
        cliente = servicio.crear_cliente(self.datos_cliente())

        self.assertEqual(cliente["id"], 1)
        self.assertEqual(cliente["rut"], "12345678-K")
        self.assertEqual(cliente["nombre"], "Gabriel")
        self.assertEqual(datos.clientes[1]["rut"], "12345678-K")

    def test_listar_clientes_devuelve_clientes_registrados(self) -> None:
        primero = servicio.crear_cliente(self.datos_cliente())
        segundo = servicio.crear_cliente(
            self.datos_cliente(
                rut="98765432-1",
                nombre="Piero",
                correo="piero@example.com",
            )
        )

        clientes = servicio.listar_clientes()

        self.assertEqual(len(clientes), 2)
        self.assertEqual(
            [cliente["id"] for cliente in clientes],
            [primero["id"], segundo["id"]],
        )

    def test_obtener_cliente_inexistente_da_404(self) -> None:
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.obtener_cliente(99)

        self.assertEqual(contexto.exception.estado_http, 404)
        self.assertEqual(contexto.exception.codigo, "RESOURCE_NOT_FOUND")

    def test_rut_duplicado_da_409(self) -> None:
        servicio.crear_cliente(self.datos_cliente())

        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.crear_cliente(
                self.datos_cliente(rut="12345678-K")
            )

        self.assertEqual(contexto.exception.estado_http, 409)
        self.assertEqual(contexto.exception.codigo, "DUPLICATE_RESOURCE")
        self.assertEqual(len(datos.clientes), 1)




SEMBRADO_CLIENTES = """
import uvicorn
from app.repositories import datos
from app.main import app

for nombre in ("vehiculos", "sucursales", "clientes", "reservas"):
    getattr(datos, nombre).clear()
for nombre in datos.contadores:
    datos.contadores[nombre] = 0

uvicorn.run(
    app,
    host="127.0.0.1",
    port=int(__import__("sys").argv[1]),
    log_level="warning",
)
"""


SEMBRADO_CLIENTES = """
import uvicorn
from app.repositories import datos
from app.main import app

for nombre in ("vehiculos", "sucursales", "clientes", "reservas"):
    getattr(datos, nombre).clear()
for nombre in datos.contadores:
    datos.contadores[nombre] = 0

uvicorn.run(
    app,
    host="127.0.0.1",
    port=int(__import__("sys").argv[1]),
    log_level="warning",
)
"""

class PruebasClientesHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]

        cls.url = f"http://127.0.0.1:{puerto}"
        cls.proceso = subprocess.Popen(
            [sys.executable, "-c", SEMBRADO_CLIENTES, str(puerto)],
            cwd=Path(__file__).resolve().parents[1],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        cls.addClassCleanup(cls.detener_servidor)

        for _ in range(100):
            try:
                with urlopen(cls.url + "/health", timeout=1) as respuesta:
                    if respuesta.status == 200:
                        return
            except (URLError, TimeoutError):
                if cls.proceso.poll() is not None:
                    raise RuntimeError(
                        "El servidor de pruebas terminó antes de iniciar"
                    )
                time.sleep(0.1)

        raise RuntimeError("El servidor de pruebas no inició a tiempo")

    @classmethod
    def detener_servidor(cls):
        cls.proceso.terminate()
        cls.proceso.wait(timeout=10)

    def solicitar(self, metodo, ruta, cuerpo=None):
        contenido = json.dumps(cuerpo).encode() if cuerpo is not None else None
        solicitud = Request(
            self.url + ruta,
            data=contenido,
            method=metodo,
            headers={"Content-Type": "application/json"},
        )

        try:
            respuesta = urlopen(solicitud, timeout=5)
        except HTTPError as error:
            respuesta = error

        with respuesta:
            contenido_respuesta = respuesta.read()
            return (
                respuesta.status,
                json.loads(contenido_respuesta) if contenido_respuesta else None,
            )

    def cuerpo(self, **cambios):
        base = {
            "rut": "12.345.678-k",
            "nombre": "Gabriel",
            "correo": "gabriel@example.com",
            "telefono": "912345678",
            "direccion": "Temuco",
        }
        return {**base, **cambios}

    def assertError(self, resultado, estado, codigo):
        status, cuerpo = resultado
        self.assertEqual(status, estado)
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(cuerpo["error"]["code"], codigo)
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_crear_listar_y_obtener_cliente(self):
        status, creado = self.solicitar("POST", "/clientes", self.cuerpo())

        self.assertEqual(status, 201)
        self.assertEqual(creado["id"], 1)
        self.assertEqual(creado["rut"], "12345678-K")
        self.assertEqual(creado["nombre"], "Gabriel")
        self.assertEqual(creado["correo"], "gabriel@example.com")

        status, lista = self.solicitar("GET", "/clientes")
        self.assertEqual(status, 200)
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0], creado)

        status, obtenido = self.solicitar("GET", "/clientes/1")
        self.assertEqual(status, 200)
        self.assertEqual(obtenido, creado)

    
    def test_rut_duplicado_da_409(self):
        rut_unico = "98765432-1"

        status, creado = self.solicitar(
            "POST",
            "/clientes",
            self.cuerpo(rut=rut_unico),
        )
        self.assertEqual(status, 201)

        self.assertError(
            self.solicitar(
                "POST",
                "/clientes",
                self.cuerpo(rut="98.765.432-1"),
            ),
            409,
            "DUPLICATE_RESOURCE",
        )


    def test_cliente_inexistente_da_404(self):
        self.assertError(
            self.solicitar("GET", "/clientes/999"),
            404,
            "RESOURCE_NOT_FOUND",
        )

    
    def test_datos_invalidos_dan_422(self):
        datos_invalidos = self.cuerpo()
        datos_invalidos.pop("correo")

        status, respuesta = self.solicitar(
            "POST",
            "/clientes",
            datos_invalidos,
        )

        self.assertEqual(status, 422)
        self.assertEqual(set(respuesta), {"error"})
        self.assertEqual(
            respuesta["error"]["code"],
            "VALIDATION_ERROR",
        )
        self.assertIsInstance(respuesta["error"]["details"], list)


if __name__ == "__main__":
    unittest.main()
