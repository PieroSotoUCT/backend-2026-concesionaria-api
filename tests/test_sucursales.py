"""Pruebas del módulo de sucursales."""

import json
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.errores import ErrorAplicacion
from app.repositories import datos
from app.services import sucursales as servicio


def reiniciar_datos() -> None:
    """Limpia las colecciones compartidas antes de cada prueba."""
    for nombre in ("vehiculos", "sucursales", "clientes", "reservas"):
        getattr(datos, nombre).clear()

    for nombre in datos.contadores:
        datos.contadores[nombre] = 0


class PruebasServicioSucursales(unittest.TestCase):
    def setUp(self) -> None:
        reiniciar_datos()

    def tearDown(self) -> None:
        reiniciar_datos()

    def datos_sucursal(self, **cambios: str) -> dict[str, str]:
        """Construye los datos de una sucursal para las pruebas."""
        base = {
            "nombre": "Sucursal Centro",
            "direccion": "Av. Alemania 123",
            "ciudad": "Temuco",
            "telefono": "452123456",
            "horario_atencion": "Lunes a viernes de 09:00 a 18:00",
        }
        return {**base, **cambios}

    def test_crear_sucursal_asigna_id_y_guarda_registro(self) -> None:
        sucursal = servicio.crear_sucursal(self.datos_sucursal())

        self.assertEqual(sucursal["id"], 1)
        self.assertEqual(sucursal["nombre"], "Sucursal Centro")
        self.assertEqual(sucursal["ciudad"], "Temuco")
        self.assertEqual(datos.sucursales[1], sucursal)

    def test_listar_sucursales_devuelve_sucursales_registradas(self) -> None:
        primera = servicio.crear_sucursal(self.datos_sucursal())
        segunda = servicio.crear_sucursal(
            self.datos_sucursal(
                nombre="Sucursal Norte",
                ciudad="Concepción",
            )
        )

        sucursales = servicio.listar_sucursales()

        self.assertEqual(len(sucursales), 2)
        self.assertEqual(
            [sucursal["id"] for sucursal in sucursales],
            [primera["id"], segunda["id"]],
        )

    def test_obtener_sucursal_existente(self) -> None:
        creada = servicio.crear_sucursal(self.datos_sucursal())

        obtenida = servicio.obtener_sucursal(creada["id"])

        self.assertEqual(obtenida, creada)

    def test_obtener_sucursal_inexistente_da_404(self) -> None:
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.obtener_sucursal(99)

        self.assertEqual(contexto.exception.estado_http, 404)
        self.assertEqual(
            contexto.exception.codigo,
            "RESOURCE_NOT_FOUND",
        )



SEMBRADO_SUCURSALES = """
import sys
import uvicorn

from app.repositories import datos

datos.sucursales.clear()
datos.contadores["sucursales"] = 0

uvicorn.run(
    "app.main:app",
    host="127.0.0.1",
    port=int(sys.argv[1]),
    log_level="critical",
)
"""


class PruebasSucursalesHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]

        cls.url = f"http://127.0.0.1:{puerto}"
        cls.proceso = subprocess.Popen(
            [sys.executable, "-c", SEMBRADO_SUCURSALES, str(puerto)],
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
            "nombre": "Sucursal Centro",
            "direccion": "Av. Alemania 123",
            "ciudad": "Temuco",
            "telefono": "452123456",
            "horario_atencion": "Lunes a viernes de 09:00 a 18:00",
        }
        return {**base, **cambios}

    def assertError(self, resultado, estado, codigo):
        status, cuerpo = resultado
        self.assertEqual(status, estado)
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(cuerpo["error"]["code"], codigo)
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_crear_listar_y_obtener_sucursal(self):
        status, creada = self.solicitar(
            "POST", "/sucursales", self.cuerpo()
        )

        self.assertEqual(status, 201)
        self.assertEqual(creada["id"], 1)
        self.assertEqual(creada["nombre"], "Sucursal Centro")
        self.assertEqual(creada["ciudad"], "Temuco")

        status, lista = self.solicitar("GET", "/sucursales")
        self.assertEqual(status, 200)
        self.assertEqual(len(lista), 1)
        self.assertEqual(lista[0], creada)

        status, obtenida = self.solicitar(
            "GET", f"/sucursales/{creada['id']}"
        )
        self.assertEqual(status, 200)
        self.assertEqual(obtenida, creada)

    def test_sucursal_inexistente_da_404(self):
        self.assertError(
            self.solicitar("GET", "/sucursales/999"),
            404,
            "RESOURCE_NOT_FOUND",
        )

    def test_datos_invalidos_dan_422(self):
        datos_invalidos = self.cuerpo()
        datos_invalidos.pop("ciudad")

        self.assertError(
            self.solicitar("POST", "/sucursales", datos_invalidos),
            422,
            "VALIDATION_ERROR",
        )


if __name__ == "__main__":
    unittest.main()
