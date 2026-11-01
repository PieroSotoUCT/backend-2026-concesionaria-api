"""Comprueba migracion, integridad y uso de una misma base por HTTP."""

import json
import socket
import subprocess
import sys
import time
import unittest
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from tests.soporte_bd import entorno_base_temporal


RAIZ = Path(__file__).resolve().parents[1]


class PruebasBasePiero(unittest.TestCase):
    def test_migracion_integridad_y_http(self):
        with entorno_base_temporal() as (entorno, ruta):
            subprocess.run(
                [sys.executable, "-c", "import app.main"],
                cwd=RAIZ, env=entorno, check=True, capture_output=True, text=True,
            )
            self.assertFalse(ruta.exists(), "Importar la API no debe crear la base")

            subprocess.run(
                [sys.executable, "-m", "alembic", "upgrade", "head"],
                cwd=RAIZ, env=entorno, check=True, capture_output=True, text=True,
            )
            verificacion = """
from sqlalchemy import inspect, text
from sqlalchemy.exc import IntegrityError
from app.db import SessionLocal, engine
from app.models import Sucursal, Vehiculo

assert set(inspect(engine).get_table_names()) >= {
    'sucursales', 'clientes', 'vehiculos', 'reservas', 'alembic_version'
}
with engine.connect() as conexion:
    assert conexion.scalar(text('PRAGMA foreign_keys')) == 1
    for tabla, referencias in {
        'vehiculos': {'sucursales'},
        'reservas': {'clientes', 'vehiculos'},
    }.items():
        reales = {fk['referred_table'] for fk in inspect(conexion).get_foreign_keys(tabla)}
        assert reales == referencias, (tabla, reales)
try:
    with SessionLocal.begin() as session:
        session.add(Vehiculo(marca='X', modelo='Y', anio=2020, precio=1,
            kilometraje=0, transmision='manual', condicion='usado',
            estado='disponible', sucursal_id=9999))
        session.flush()
except IntegrityError:
    pass
else:
    raise AssertionError('SQLite acepto una sucursal inexistente')
with SessionLocal.begin() as session:
    session.add(Sucursal(nombre='Fixture ORM', direccion='A', ciudad='Temuco',
        telefono='1', horario_atencion='9-18'))
"""
            subprocess.run(
                [sys.executable, "-c", verificacion],
                cwd=RAIZ, env=entorno, check=True, capture_output=True, text=True,
            )

            with socket.socket() as conexion:
                conexion.bind(("127.0.0.1", 0))
                puerto = conexion.getsockname()[1]
            url = f"http://127.0.0.1:{puerto}"
            proceso = subprocess.Popen(
                [sys.executable, "-m", "uvicorn", "app.main:app", "--host",
                 "127.0.0.1", "--port", str(puerto)],
                cwd=RAIZ, env=entorno, stdout=subprocess.DEVNULL,
                stderr=subprocess.STDOUT,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0,
            )
            try:
                for _ in range(100):
                    try:
                        with urlopen(url + "/sucursales", timeout=1) as respuesta:
                            self.assertEqual(respuesta.status, 200)
                            cuerpo = json.load(respuesta)
                            self.assertIn("Fixture ORM", str(cuerpo))
                            break
                    except (URLError, TimeoutError):
                        if proceso.poll() is not None:
                            self.fail("El servidor de prueba termino antes de responder")
                        time.sleep(0.1)
                else:
                    self.fail("El servidor de prueba no inicio a tiempo")
            finally:
                proceso.terminate()
                proceso.wait(timeout=10)
