
"""Pruebas del módulo de clientes."""

import unittest

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


if __name__ == "__main__":
    unittest.main()
