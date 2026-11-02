"""Pruebas aisladas del módulo de clientes."""

import os
import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy import create_engine, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# La variable se configura antes de importar la aplicación.
# SQLite en memoria evita utilizar concesionaria.db.
os.environ["CONCESIONARIA_DATABASE_URL"] = "sqlite://"

from app.db import Base
from app.db import engine as motor_aplicacion
from app.models import Cliente
from app.services.clientes import _es_rut_duplicado

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

# Se importa la aplicación después de configurar el entorno.
from app.main import app

cliente_http = TestClient(app)


class PruebasClientes(unittest.TestCase):
    """Pruebas de servicio y endpoints de clientes."""

    @classmethod
    def tearDownClass(cls) -> None:
        """Cierra las conexiones de las bases de datos de prueba."""
        cliente_http.close()
        motor_pruebas.dispose()
        motor_aplicacion.dispose()

    def setUp(self) -> None:
        Base.metadata.create_all(bind=motor_pruebas)

        self.parche_clientes = patch(
            "app.services.clientes.SessionLocal",
            SesionPruebas,
        )
        self.parche_sucursales = patch(
            "app.services.sucursales.SessionLocal",
            SesionPruebas,
        )

        self.parche_clientes.start()
        self.parche_sucursales.start()

        self.addCleanup(self.parche_clientes.stop)
        self.addCleanup(self.parche_sucursales.stop)

        with SesionPruebas.begin() as session:
            session.execute(delete(Cliente))

        self.client = cliente_http

    def tearDown(self) -> None:
        with SesionPruebas.begin() as session:
            session.execute(delete(Cliente))

    def datos_cliente(self, **cambios: str) -> dict[str, str]:
        """Construye datos válidos para registrar un cliente."""
        base = {
            "rut": "12.345.678-k",
            "nombre": "Gabriel",
            "correo": "gabriel@example.com",
            "telefono": "912345678",
            "direccion": "Temuco",
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

    def test_crear_cliente_normaliza_rut(self) -> None:
        respuesta = self.client.post(
            "/clientes",
            json=self.datos_cliente(),
        )

        self.assertEqual(respuesta.status_code, 201)
        cliente = respuesta.json()

        self.assertGreater(cliente["id"], 0)
        self.assertEqual(cliente["rut"], "12345678-K")
        self.assertEqual(cliente["nombre"], "Gabriel")
        self.assertEqual(cliente["correo"], "gabriel@example.com")

    def test_listar_clientes(self) -> None:
        creado = self.client.post(
            "/clientes",
            json=self.datos_cliente(),
        )
        self.assertEqual(creado.status_code, 201)

        respuesta = self.client.get("/clientes")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(len(respuesta.json()), 1)
        self.assertEqual(
            respuesta.json()[0]["rut"],
            "12345678-K",
        )

    def test_obtener_cliente_existente(self) -> None:
        creado = self.client.post(
            "/clientes",
            json=self.datos_cliente(),
        )
        cliente = creado.json()

        respuesta = self.client.get(f"/clientes/{cliente['id']}")

        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(respuesta.json(), cliente)

    def test_cliente_inexistente_da_404(self) -> None:
        respuesta = self.client.get("/clientes/999999")

        self.assert_error(
            respuesta,
            404,
            "RESOURCE_NOT_FOUND",
        )

    def test_rut_duplicado_da_409(self) -> None:
        primera_respuesta = self.client.post(
            "/clientes",
            json=self.datos_cliente(),
        )
        self.assertEqual(primera_respuesta.status_code, 201)

        segunda_respuesta = self.client.post(
            "/clientes",
            json=self.datos_cliente(rut="12345678-K"),
        )

        self.assert_error(
            segunda_respuesta,
            409,
            "DUPLICATE_RESOURCE",
        )

    def test_integrity_error_por_rut_duplicado_da_409_y_hace_rollback(
        self,
    ) -> None:
        """Comprueba el conflicto real de unicidad y el rollback."""
        with SesionPruebas.begin() as session:
            cliente_existente = Cliente(
                rut="12345678-K",
                nombre="Cliente Existente",
                correo="existente@example.com",
                telefono="912345678",
                direccion="Temuco",
            )
            session.add(cliente_existente)

        # Simula que la consulta previa no detectó el duplicado.
        # La restricción UNIQUE de SQLite debe rechazar la inserción.
        with patch(
            "app.services.clientes.repositorio_clientes.buscar_por_rut",
            return_value=None,
        ):
            respuesta = self.client.post(
                "/clientes",
                json=self.datos_cliente(rut="12345678-K"),
            )

        self.assert_error(
            respuesta,
            409,
            "DUPLICATE_RESOURCE",
        )

        # El registro original debe permanecer y no debe existir
        # una segunda inserción después del rollback.
        with SesionPruebas() as session:
            clientes = session.query(Cliente).all()

            self.assertEqual(len(clientes), 1)
            self.assertEqual(clientes[0].nombre, "Cliente Existente")
            self.assertEqual(clientes[0].rut, "12345678-K")

    def test_integrity_error_identifica_solo_duplicado_de_rut(
        self,
    ) -> None:
        """Distingue duplicados de RUT de otros errores de integridad."""
        error_rut = IntegrityError(
            "INSERT",
            {},
            Exception("UNIQUE constraint failed: clientes.rut"),
        )

        error_nombre = IntegrityError(
            "INSERT",
            {},
            Exception("NOT NULL constraint failed: clientes.nombre"),
        )

        self.assertTrue(_es_rut_duplicado(error_rut))
        self.assertFalse(_es_rut_duplicado(error_nombre))

    def test_correo_invalido_da_422(self) -> None:
        respuesta = self.client.post(
            "/clientes",
            json=self.datos_cliente(correo="correo-invalido"),
        )

        self.assert_error(
            respuesta,
            422,
            "VALIDATION_ERROR",
        )

    def test_datos_faltantes_dan_422(self) -> None:
        datos = self.datos_cliente()
        datos.pop("correo")

        respuesta = self.client.post(
            "/clientes",
            json=datos,
        )

        self.assert_error(
            respuesta,
            422,
            "VALIDATION_ERROR",
        )


if __name__ == "__main__":
    unittest.main()
