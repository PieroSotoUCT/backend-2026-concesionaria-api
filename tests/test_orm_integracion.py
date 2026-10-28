"""Pruebas de persistencia ORM y atomicidad entre reservas y vehiculos."""

import unittest
from datetime import date, timedelta

from app.db import SessionLocal
from app.errores import ErrorAplicacion
from app.models import Cliente, Reserva, Sucursal, Vehiculo
from app.repositories.datos import limpiar_base
from app.schemas.reserva import ReservaCrear
from app.services.reservas import crear_reserva


class PruebasORMIntegracion(unittest.TestCase):
    def setUp(self):
        limpiar_base()
        with SessionLocal.begin() as session:
            sucursal = Sucursal(nombre="Centro", direccion="A", ciudad="Temuco",
                                telefono="1", horario_atencion="9-18")
            session.add(sucursal)
            session.flush()
            cliente = Cliente(rut="1-9", nombre="Ana", correo="ana@example.com",
                              telefono="1", direccion="A")
            session.add(cliente)
            session.flush()
            session.add(Vehiculo(
                marca="Toyota", modelo="Yaris", anio=2022, precio=100,
                kilometraje=0, transmision="manual", condicion="usado",
                estado="disponible", sucursal_id=sucursal.id,
            ))

    def tearDown(self):
        limpiar_base()

    def test_reserva_persiste_y_actualiza_relacion(self):
        reserva = crear_reserva(ReservaCrear(
            cliente_id=1, vehiculo_id=1,
            fecha_vencimiento=date.today() + timedelta(days=1),
            monto_reserva=10,
        ))
        with SessionLocal() as session:
            self.assertEqual(session.get(Reserva, reserva["id"]).estado, "activa")
            self.assertEqual(session.get(Vehiculo, 1).estado, "reservado")

    def test_error_antes_de_escribir_hace_rollback(self):
        with self.assertRaises(ErrorAplicacion):
            crear_reserva(ReservaCrear(
                cliente_id=999, vehiculo_id=1,
                fecha_vencimiento=date.today() + timedelta(days=1),
                monto_reserva=10,
            ))
        with SessionLocal() as session:
            self.assertEqual(session.query(Reserva).count(), 0)
            self.assertEqual(session.get(Vehiculo, 1).estado, "disponible")
