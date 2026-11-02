"""Pruebas ORM y HTTP del modulo de reservas sobre una SQLite temporal."""

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

from sqlalchemy import select

from app.db import SessionLocal, engine
from app.errores import ErrorAplicacion
from app.models import Cliente, Reserva, Sucursal, Vehiculo
from app.repositories.datos import limpiar_base
from app.schemas.reserva import ReservaCrear
from app.services import reservas as servicio


def _limpiar_archivos_temporales() -> None:
    engine.dispose()
    for sufijo in ("", "-journal", "-wal", "-shm"):
        Path(f"{TEST_DATABASE_PATH}{sufijo}").unlink(missing_ok=True)


atexit.register(_limpiar_archivos_temporales)

SEMBRADO = """
import sys
from datetime import date, timedelta
import uvicorn
from app.db import SessionLocal
from app.main import app
from app.models import Cliente, Reserva, Sucursal, Vehiculo

with SessionLocal.begin() as session:
    sucursal = Sucursal(nombre="Centro", direccion="A", ciudad="Temuco",
                        telefono="1", horario_atencion="9-18")
    cliente = Cliente(rut="1-9", nombre="Ana", correo="ana@example.com",
                      telefono="1", direccion="A")
    session.add_all([sucursal, cliente])
    session.flush()
    vehiculos = []
    for estado in ("disponible", "disponible", "reservado", "vendido"):
        vehiculo = Vehiculo(
            marca="Toyota", modelo="Yaris", anio=2022, precio=10000000,
            kilometraje=1, transmision="manual", condicion="usado",
            estado=estado, sucursal_id=sucursal.id,
        )
        session.add(vehiculo)
        vehiculos.append(vehiculo)
    session.flush()
    session.add(Reserva(
        cliente_id=cliente.id, vehiculo_id=vehiculos[2].id,
        fecha_reserva=date.today() - timedelta(days=10),
        fecha_vencimiento=date.today() - timedelta(days=1),
        monto_reserva=100000, estado="activa",
    ))

uvicorn.run(app, host="127.0.0.1", port=int(sys.argv[1]), log_level="warning")
"""


def sembrar_servicio() -> tuple[int, list[int]]:
    limpiar_base()
    with SessionLocal.begin() as session:
        sucursal = Sucursal(nombre="Centro", direccion="A", ciudad="Temuco",
                            telefono="1", horario_atencion="9-18")
        cliente = Cliente(rut="1-9", nombre="Ana", correo="ana@example.com",
                          telefono="1", direccion="A")
        session.add_all([sucursal, cliente])
        session.flush()
        vehiculos = [
            Vehiculo(
                marca="Toyota", modelo="Yaris", anio=2022, precio=10000000,
                kilometraje=1, transmision="manual", condicion="usado",
                estado=estado, sucursal_id=sucursal.id,
            )
            for estado in ("disponible", "disponible", "reservado", "vendido")
        ]
        session.add_all(vehiculos)
        session.flush()
        return cliente.id, [vehiculo.id for vehiculo in vehiculos]


def entrada(cliente_id: int, vehiculo_id: int, **cambios: object) -> ReservaCrear:
    base = {
        "cliente_id": cliente_id,
        "vehiculo_id": vehiculo_id,
        "fecha_vencimiento": date.today() + timedelta(days=7),
        "monto_reserva": 500000,
    }
    return ReservaCrear(**{**base, **cambios})


def insertar_reserva(
    cliente_id: int,
    vehiculo_id: int,
    fecha_vencimiento: date,
    fecha_reserva: date | None = None,
) -> int:
    with SessionLocal.begin() as session:
        reserva = Reserva(
            cliente_id=cliente_id,
            vehiculo_id=vehiculo_id,
            fecha_reserva=fecha_reserva or date.today(),
            fecha_vencimiento=fecha_vencimiento,
            monto_reserva=500000,
            estado="activa",
        )
        session.add(reserva)
        session.flush()
        return reserva.id


class PruebasServicioReservas(unittest.TestCase):
    def setUp(self):
        self.cliente_id, self.vehiculo_ids = sembrar_servicio()

    def _estado_vehiculo(self, vehiculo_id: int) -> str:
        with SessionLocal() as session:
            return session.get(Vehiculo, vehiculo_id).estado

    def _estado_reserva(self, reserva_id: int) -> str:
        with SessionLocal() as session:
            return session.get(Reserva, reserva_id).estado

    def test_crear_reserva_marca_vehiculo_reservado(self):
        reserva = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        self.assertEqual(reserva["estado"], "activa")
        self.assertEqual(reserva["fecha_reserva"], date.today())
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "reservado")

    def test_reservar_hoy_es_valido(self):
        reserva = servicio.crear_reserva(entrada(
            self.cliente_id, self.vehiculo_ids[0], fecha_vencimiento=date.today(),
        ))
        self.assertEqual(reserva["estado"], "activa")

    def test_cliente_o_vehiculo_inexistente_da_404_sin_efectos(self):
        for cambios in ({"cliente_id": 999}, {"vehiculo_id": 999}):
            datos = entrada(
                self.cliente_id, self.vehiculo_ids[0],
            ).model_dump()
            datos.update(cambios)
            with self.assertRaises(ErrorAplicacion) as contexto:
                servicio.crear_reserva(ReservaCrear(**datos))
            self.assertEqual(contexto.exception.estado_http, 404)
        with SessionLocal() as session:
            self.assertEqual(session.scalar(select(Reserva.id)), None)
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "disponible")

    def test_fecha_anterior_a_hoy_da_400(self):
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.crear_reserva(entrada(
                self.cliente_id, self.vehiculo_ids[0],
                fecha_vencimiento=date.today() - timedelta(days=1),
            ))
        self.assertEqual(contexto.exception.estado_http, 400)
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "disponible")

    def test_vehiculo_reservado_o_vendido_da_409(self):
        servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        for vehiculo_id in (self.vehiculo_ids[0], self.vehiculo_ids[3]):
            with self.assertRaises(ErrorAplicacion) as contexto:
                servicio.crear_reserva(entrada(self.cliente_id, vehiculo_id))
            self.assertEqual(contexto.exception.estado_http, 409)
            self.assertEqual(contexto.exception.codigo, "VEHICLE_NOT_AVAILABLE")
        with SessionLocal() as session:
            activas = session.scalars(
                select(Reserva).where(
                    Reserva.vehiculo_id == self.vehiculo_ids[0],
                    Reserva.estado == "activa",
                )
            ).all()
            self.assertEqual(len(activas), 1)
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "reservado")

    def test_reserva_activa_impide_duplicado_aunque_vehiculo_diga_disponible(self):
        insertar_reserva(
            self.cliente_id, self.vehiculo_ids[0], date.today() + timedelta(days=1),
        )
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        self.assertEqual(contexto.exception.estado_http, 409)
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "disponible")

    def test_cancelar_libera_vehiculo(self):
        reserva = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        cancelada = servicio.cancelar_reserva(reserva["id"])
        self.assertEqual(cancelada["estado"], "cancelada")
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "disponible")

    def test_cancelar_dos_veces_da_409_y_no_existente_404(self):
        reserva = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        servicio.cancelar_reserva(reserva["id"])
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(reserva["id"])
        self.assertEqual(contexto.exception.estado_http, 409)
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(999)
        self.assertEqual(contexto.exception.estado_http, 404)

    def test_vencimiento_libera_vehiculo_y_es_idempotente(self):
        reserva = servicio.crear_reserva(entrada(
            self.cliente_id, self.vehiculo_ids[0],
            fecha_vencimiento=date.today() + timedelta(days=2),
        ))
        self.assertEqual(servicio.procesar_vencimientos(date.today() + timedelta(days=2)), 0)
        self.assertEqual(self._estado_reserva(reserva["id"]), "activa")
        limite_superado = date.today() + timedelta(days=3)
        self.assertEqual(servicio.procesar_vencimientos(limite_superado), 1)
        self.assertEqual(self._estado_reserva(reserva["id"]), "vencida")
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "disponible")
        self.assertEqual(servicio.procesar_vencimientos(limite_superado), 0)

    def test_vencimiento_no_toca_canceladas_ni_vehiculos_vendidos(self):
        reserva = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        servicio.cancelar_reserva(reserva["id"])
        reserva_vendida_id = insertar_reserva(
            self.cliente_id, self.vehiculo_ids[3],
            date.today() - timedelta(days=1),
        )
        self.assertEqual(servicio.procesar_vencimientos(date.today()), 1)
        self.assertEqual(self._estado_reserva(reserva["id"]), "cancelada")
        self.assertEqual(self._estado_reserva(reserva_vendida_id), "vencida")
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[3]), "vendido")

    def test_vencimiento_no_libera_si_queda_otra_reserva_activa(self):
        vehiculo_id = self.vehiculo_ids[1]
        with SessionLocal.begin() as session:
            session.get(Vehiculo, vehiculo_id).estado = "reservado"
        vencida_id = insertar_reserva(
            self.cliente_id, vehiculo_id, date.today() - timedelta(days=1),
        )
        insertar_reserva(
            self.cliente_id, vehiculo_id, date.today() + timedelta(days=1),
        )
        self.assertEqual(servicio.procesar_vencimientos(date.today()), 1)
        self.assertEqual(self._estado_reserva(vencida_id), "vencida")
        self.assertEqual(self._estado_vehiculo(vehiculo_id), "reservado")

    def test_error_al_cancelar_revierte_vencimientos_de_la_operacion(self):
        vehiculo_id = self.vehiculo_ids[0]
        with SessionLocal.begin() as session:
            session.get(Vehiculo, vehiculo_id).estado = "reservado"
        reserva_id = insertar_reserva(
            self.cliente_id, vehiculo_id, date.today() - timedelta(days=1),
        )
        with self.assertRaises(ErrorAplicacion) as contexto:
            servicio.cancelar_reserva(reserva_id)
        self.assertEqual(contexto.exception.estado_http, 409)
        self.assertEqual(self._estado_reserva(reserva_id), "activa")
        self.assertEqual(self._estado_vehiculo(vehiculo_id), "reservado")
        self.assertEqual(servicio.procesar_vencimientos(date.today()), 1)
        self.assertEqual(self._estado_reserva(reserva_id), "vencida")
        self.assertEqual(self._estado_vehiculo(vehiculo_id), "disponible")

    def test_listar_ordena_por_id_y_procesa_vencimientos(self):
        primera = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        segunda = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[1]))
        with SessionLocal.begin() as session:
            session.get(Reserva, primera["id"]).fecha_vencimiento = (
                date.today() - timedelta(days=1)
            )
        lista = servicio.listar_reservas()
        self.assertEqual(
            [reserva["id"] for reserva in lista],
            sorted((primera["id"], segunda["id"])),
        )
        estados = {reserva["id"]: reserva["estado"] for reserva in lista}
        self.assertEqual(estados[primera["id"]], "vencida")
        self.assertEqual(estados[segunda["id"]], "activa")

    def test_vehiculo_liberado_puede_reservarse_de_nuevo(self):
        primera = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        servicio.cancelar_reserva(primera["id"])
        nueva = servicio.crear_reserva(entrada(self.cliente_id, self.vehiculo_ids[0]))
        self.assertNotEqual(nueva["id"], primera["id"])
        self.assertEqual(self._estado_vehiculo(self.vehiculo_ids[0]), "reservado")


class PruebasReservasHTTP(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        limpiar_base()
        with socket.socket() as conexion:
            conexion.bind(("127.0.0.1", 0))
            puerto = conexion.getsockname()[1]
        cls.url = f"http://127.0.0.1:{puerto}"
        cls.proceso = subprocess.Popen(
            [sys.executable, "-c", SEMBRADO, str(puerto)],
            cwd=PROJECT_ROOT,
            env=os.environ.copy(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.STDOUT,
        )
        cls.addClassCleanup(limpiar_base)
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
        if cls.proceso.poll() is None:
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
            cuerpo_respuesta = respuesta.read()
            return (
                respuesta.status,
                json.loads(cuerpo_respuesta) if cuerpo_respuesta else None,
            )

    def vehiculos(self):
        status, respuesta = self.solicitar("GET", "/vehiculos")
        self.assertEqual(status, 200)
        return respuesta["items"]

    def vehiculo_id(self, estado):
        return next(v["id"] for v in self.vehiculos() if v["estado"] == estado)

    def cuerpo(self, **cambios):
        base = {
            "cliente_id": 1,
            "vehiculo_id": self.vehiculo_id("disponible"),
            "fecha_vencimiento": (date.today() + timedelta(days=5)).isoformat(),
            "monto_reserva": 450000,
        }
        return {**base, **cambios}

    def assertError(self, resultado, estado, codigo):
        status, cuerpo = resultado
        self.assertEqual(status, estado)
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(cuerpo["error"]["code"], codigo)
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_flujo_completo_y_formato_de_errores(self):
        status, reservas = self.solicitar("GET", "/reservas")
        self.assertEqual(status, 200)
        vencida = next(reserva for reserva in reservas if reserva["estado"] == "vencida")
        status, detalle = self.solicitar("GET", f"/reservas/{vencida['id']}")
        self.assertEqual((status, detalle["estado"]), (200, "vencida"))

        cuerpo = self.cuerpo()
        status, creada = self.solicitar("POST", "/reservas", cuerpo)
        self.assertEqual(status, 201)
        self.assertEqual(creada["estado"], "activa")
        self.assertEqual(creada["fecha_reserva"], date.today().isoformat())
        self.assertEqual(
            self.solicitar("GET", f"/reservas/{creada['id']}")[1],
            creada,
        )

        self.assertError(
            self.solicitar("POST", "/reservas", cuerpo),
            409,
            "VEHICLE_NOT_AVAILABLE",
        )
        status, lista = self.solicitar("GET", "/reservas")
        self.assertEqual(status, 200)
        self.assertEqual([r["id"] for r in lista], sorted(r["id"] for r in lista))

        status, cancelada = self.solicitar(
            "PATCH", f"/reservas/{creada['id']}", {"estado": "cancelada"},
        )
        self.assertEqual((status, cancelada["estado"]), (200, "cancelada"))
        self.assertError(
            self.solicitar("PATCH", f"/reservas/{creada['id']}",
                           {"estado": "cancelada"}),
            409,
            "STATE_CONFLICT",
        )
        self.assertEqual(self.solicitar("POST", "/reservas", cuerpo)[0], 201)

    def test_errores_de_negocio(self):
        self.assertError(
            self.solicitar("POST", "/reservas", self.cuerpo(cliente_id=999)),
            404,
            "RESOURCE_NOT_FOUND",
        )
        self.assertError(
            self.solicitar("POST", "/reservas", self.cuerpo(vehiculo_id=999)),
            404,
            "RESOURCE_NOT_FOUND",
        )
        ayer = (date.today() - timedelta(days=1)).isoformat()
        self.assertError(
            self.solicitar(
                "POST", "/reservas",
                self.cuerpo(fecha_vencimiento=ayer),
            ),
            400,
            "INVALID_EXPIRATION_DATE",
        )
        self.assertError(
            self.solicitar(
                "POST", "/reservas",
                self.cuerpo(vehiculo_id=self.vehiculo_id("vendido")),
            ),
            409,
            "VEHICLE_NOT_AVAILABLE",
        )
        self.assertError(
            self.solicitar("GET", "/reservas/999"),
            404,
            "RESOURCE_NOT_FOUND",
        )
        self.assertError(
            self.solicitar("PATCH", "/reservas/999", {"estado": "cancelada"}),
            404,
            "RESOURCE_NOT_FOUND",
        )

    def test_validaciones_422(self):
        casos = [
            self.cuerpo(monto_reserva=0),
            self.cuerpo(monto_reserva="500"),
            self.cuerpo(cliente_id=0),
            self.cuerpo(vehiculo_id="1"),
            self.cuerpo(fecha_vencimiento="manana"),
            self.cuerpo(id=7),
            self.cuerpo(estado="activa"),
            self.cuerpo(fecha_reserva="2026-01-01"),
        ]
        sin_campo = self.cuerpo()
        del sin_campo["monto_reserva"]
        casos.append(sin_campo)
        for caso in casos:
            self.assertError(
                self.solicitar("POST", "/reservas", caso),
                422,
                "VALIDATION_ERROR",
            )
        for ruta in ("/reservas/0", "/reservas/abc"):
            self.assertError(
                self.solicitar("GET", ruta),
                422,
                "VALIDATION_ERROR",
            )
        for cuerpo in (
            {"estado": "activa"},
            {"estado": "vencida"},
            {"estado": None},
            {},
            {"estado": "cancelada", "monto_reserva": 1},
        ):
            self.assertError(
                self.solicitar("PATCH", "/reservas/999", cuerpo),
                422,
                "VALIDATION_ERROR",
            )


if __name__ == "__main__":
    unittest.main()
