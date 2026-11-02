
"""Pruebas aisladas del módulo de sucursales."""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Configura SQLite en memoria antes de importar la aplicación.
os.environ["CONCESIONARIA_DATABASE_URL"] = "sqlite://"

from app.db import Base  # noqa: E402
from app.models import Sucursal  # noqa: E402

motor_pruebas = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

SesionPruebas = sessionmaker(
    bind=motor_pruebas,
    autoflush=False,
    expire_on_commit=False,
)

# Importa la aplicación después de configurar el entorno.
from app.main import app  # noqa: E402

cliente_http = TestClient(app)


class PruebasSucursales(unittest.TestCase):
    """Pruebas de servicio y endpoints de sucursales."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Cierra las conexiones de la base de datos de prueba."""
        cliente_http.close()
        motor_pruebas.dispose()

    def setUp(self) -> None:
        Base.metadata.create_all(bind=motor_pruebas)

        self.parche_sucursales = patch(
            "app.services.sucursales.SessionLocal",
            SesionPruebas,
        )
        self.parche_clientes = patch(
            "app.services.clientes.SessionLocal",
            SesionPruebas,
        )

        self.parche_sucursales.start()
        self.parche_clientes.start()

        self.addCleanup(self.parche_sucursales.stop)
        self.addCleanup(self.parche_clientes.stop)

        with SesionPruebas.begin() as session:
            session.execute(delete(Sucursal))

        self.client = cliente_http

    def tearDown(self) -> None:
        with SesionPruebas.begin() as session:
            session.execute(delete(Sucursal))

    def datos_sucursal(self, **cambios: str) -> dict[str, str]:
        """Construye datos válidos para registrar una sucursal."""
        base = {
            "nombre": "Sucursal Centro",
            "direccion": "Av. Alemania 123",
            "ciudad": "Temuco",
            "telefono": "452123456",
            "horario_atencion": "Lunes a viernes de 09:00 a 18:00",
        }
        return {**base, **cambios}

    def assert_error(
        self,
        respuesta,
        estado: int,
        codigo: str,
    ) -> None:
        """Comprueba la estructura común de los errores HTTP."""
        self.assertEqual(respuesta.status_code, estado)

        cuerpo = respuesta.json()
        self.assertEqual(set(cuerpo), {"error"})
        self.assertEqual(cuerpo["error"]["code"], codigo)
        self.assertIsInstance(cuerpo["error"]["details"], list)

    def test_crear_sucursal_asigna_id(self) -> None:
        respuesta = self.client.post(
            "/sucursales",
            json=self.datos_sucursal(),
        )

        self.assertEqual(respuesta.status_code, 201)
        sucursal = respuesta.json()

        self.assertGreater(sucursal["id"], 0)
        self.assertEqual(sucursal["nombre"], "Sucursal Centro")
        self.assertEqual(sucursal["ciudad"], "Temuco")

    def test_listar_sucursales(self) -> None:
        creada = self.client.post(
            "/sucursales",
            json=self.datos_sucursal(),
        )
        self.assertEqual(creada.status_code, 201)

        respuesta = self.client.get("/sucursales")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(
            respuesta.json()[0]["nombre"],
            "Sucursal Centro",
        )

    def test_obtener_sucursal_existente(self) -> None:
        creada = self.client.post(
            "/sucursales",
            json=self.datos_sucursal(),
        )
        sucursal = creada.json()

        respuesta = self.client.get(
            f"/sucursales/{sucursal['id']}"
        )

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), sucursal)

    def test_obtener_sucursal_inexistente_da_404(self) -> None:
        respuesta = self.client.get("/sucursales/999999")

        self.assert_error(
            respuesta,
            404,
            "RESOURCE_NOT_FOUND",
        )

    def test_datos_invalidos_dan_422(self) -> None:
        datos = self.datos_sucursal()
        datos.pop("ciudad")

        respuesta = self.client.post(
            "/sucursales",
            json=datos,
        )

        self.assert_error(
            respuesta,
            422,
            "VALIDATION_ERROR",
        )
