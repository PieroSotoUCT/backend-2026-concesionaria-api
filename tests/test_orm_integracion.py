"""Pruebas ORM, rollback y persistencia entre procesos de la API."""

import atexit
import json
import os
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import date, timedelta
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TEST_DATABASE_PATH = Path(tempfile.gettempdir()) / f"concesionaria-tests-{os.getpid()}.db"
os.environ["CONCESIONARIA_DATABASE_URL"] = f"sqlite:///{TEST_DATABASE_PATH.as_posix()}"
os.environ.pop("CONCESIONARIA_DATOS_DEMO", None)
os.environ["PYTHONPATH"] = os.pathsep.join(
    filter(None, (str(PROJECT_ROOT), os.environ.get("PYTHONPATH", "")))
)

ALEMBIC_CLI = Path(sys.executable).with_name("alembic.exe")
if not ALEMBIC_CLI.exists():
    raise RuntimeError("Ejecuta las pruebas con .venv\\Scripts\\python.exe")
subprocess.run(
    [str(ALEMBIC_CLI), "upgrade", "head"],
    cwd=PROJECT_ROOT,
    env=os.environ.copy(),
    check=True,
)

from app.db import SessionLocal, engine
from app.errores import ErrorAplicacion
from app.models import Cliente, Reserva, Sucursal, Vehiculo
from app.repositories.datos import limpiar_base
from app.schemas.reserva import ReservaCrear
from app.services.reservas import crear_reserva


def _limpiar_archivos_temporales() -> None:
    engine.dispose()
    for sufijo in ("", "-journal", "-wal", "-shm"):
        Path(f"{TEST_DATABASE_PATH}{sufijo}").unlink(missing_ok=True)


atexit.register(_limpiar_archivos_temporales)


class PruebasORMIntegracion(unittest.TestCase):
    def setUp(self):
        limpiar_base()
        with SessionLocal.begin() as session:
            sucursal = Sucursal(nombre="Centro", direccion="A", ciudad="Temuco",
                                telefono="1", horario_atencion="9-18")
            cliente = Cliente(rut="1-9", nombre="Ana", correo="ana@example.com",
                              telefono="1", direccion="A")
            session.add_all([sucursal, cliente])
            session.flush()
            vehiculo = Vehiculo(
                marca="Toyota", modelo="Yaris", anio=2022, precio=100,
                kilometraje=0, transmision="manual", condicion="usado",
                estado="disponible", sucursal_id=sucursal.id,
            )
            session.add(vehiculo)
            session.flush()
            self.cliente_id = cliente.id
            self.vehiculo_id = vehiculo.id

    def test_reserva_persiste_y_actualiza_relacion(self):
        reserva = crear_reserva(ReservaCrear(
            cliente_id=self.cliente_id,
            vehiculo_id=self.vehiculo_id,
            fecha_vencimiento=date.today() + timedelta(days=1),
            monto_reserva=10,
        ))
        with SessionLocal() as session:
            self.assertEqual(session.get(Reserva, reserva["id"]).estado, "activa")
            self.assertEqual(session.get(Vehiculo, self.vehiculo_id).estado, "reservado")

    def test_error_despues_de_escrituras_revierten_la_transaccion(self):
        with SessionLocal.begin() as session:
            session.get(Vehiculo, self.vehiculo_id).estado = "reservado"
            reserva = Reserva(
                cliente_id=self.cliente_id,
                vehiculo_id=self.vehiculo_id,
                fecha_reserva=date.today() - timedelta(days=2),
                fecha_vencimiento=date.today() - timedelta(days=1),
                monto_reserva=10,
                estado="activa",
            )
            session.add(reserva)
            session.flush()
            reserva_id = reserva.id

        with self.assertRaises(ErrorAplicacion) as contexto:
            crear_reserva(ReservaCrear(
                cliente_id=999,
                vehiculo_id=self.vehiculo_id,
                fecha_vencimiento=date.today() + timedelta(days=1),
                monto_reserva=10,
            ))
        self.assertEqual(contexto.exception.estado_http, 404)

        with SessionLocal() as session:
            self.assertEqual(session.get(Reserva, reserva_id).estado, "activa")
            self.assertEqual(session.get(Vehiculo, self.vehiculo_id).estado, "reservado")

    def _iniciar_api(self) -> tuple[subprocess.Popen, str]:
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]
        url = f"http://127.0.0.1:{puerto}"
        proceso = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn", "app.main:app",
                "--host", "127.0.0.1", "--port", str(puerto),
                "--log-level", "warning",
            ],
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        for _ in range(100):
            try:
                with urlopen(url + "/health", timeout=1) as respuesta:
                    if respuesta.status == 200:
                        return proceso, url
            except (URLError, TimeoutError):
                if proceso.poll() is not None:
                    raise RuntimeError("El servidor de pruebas termino antes de iniciar")
                time.sleep(0.1)
        self._detener_api(proceso)
        raise RuntimeError("El servidor de pruebas no inicio a tiempo")

    @staticmethod
    def _detener_api(proceso: subprocess.Popen) -> None:
        if proceso.poll() is None:
            proceso.terminate()
            proceso.wait(timeout=10)

    @staticmethod
    def _solicitar(url: str, metodo: str, ruta: str, cuerpo=None):
        contenido = json.dumps(cuerpo).encode() if cuerpo is not None else None
        solicitud = Request(
            url + ruta,
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

    def test_persistencia_tras_reiniciar_proceso_sin_seeder(self):
        cuerpo = {
            "cliente_id": self.cliente_id,
            "vehiculo_id": self.vehiculo_id,
            "fecha_vencimiento": (date.today() + timedelta(days=1)).isoformat(),
            "monto_reserva": 10,
        }
        primer_proceso, primera_url = self._iniciar_api()
        try:
            status, creada = self._solicitar(
                primera_url, "POST", "/reservas", cuerpo,
            )
            self.assertEqual(status, 201)
        finally:
            self._detener_api(primer_proceso)

        segundo_proceso, segunda_url = self._iniciar_api()
        try:
            status, recuperada = self._solicitar(
                segunda_url, "GET", f"/reservas/{creada['id']}",
            )
            self.assertEqual(status, 200)
            self.assertEqual(recuperada, creada)
            with SessionLocal() as session:
                self.assertEqual(
                    session.get(Vehiculo, self.vehiculo_id).estado,
                    "reservado",
                )
        finally:
            self._detener_api(segundo_proceso)


if __name__ == "__main__":
    unittest.main()
