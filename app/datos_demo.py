"""Carga opcional de datos ficticios mediante ORM."""

from datetime import date, timedelta

from app.db import SessionLocal
from app.domain.vehiculo import Condicion, EstadoVehiculo, Transmision
from app.models import Cliente, Reserva, Sucursal, Vehiculo


def cargar_datos_demo() -> None:
    with SessionLocal.begin() as session:
        if session.query(Sucursal).first() or session.query(Cliente).first():
            raise RuntimeError("Los datos demo requieren iniciar con base vacia")
        sucursales = [
            Sucursal(nombre="Sucursal Centro", direccion="Avenida Ficticia 100",
                     ciudad="Temuco", telefono="56900000001",
                     horario_atencion="Lunes a viernes 09:00-18:00"),
            Sucursal(nombre="Sucursal Sur", direccion="Calle Ejemplo 200",
                     ciudad="Valdivia", telefono="56900000002",
                     horario_atencion="Lunes a viernes 09:00-18:00"),
        ]
        session.add_all(sucursales)
        cliente = Cliente(rut="00000000-0", nombre="Cliente Ficticio",
                          correo="cliente.demo@example.com", telefono="56900000003",
                          direccion="Pasaje Inventado 30")
        session.add(cliente)
        session.flush()
        datos = [
            ("Toyota", "Yaris", 2022, 10990000, 23000, Transmision.MANUAL, Condicion.USADO, "disponible", 0),
            ("Hyundai", "Tucson", 2021, 17990000, 48000, Transmision.AUTOMATICA, Condicion.USADO, "disponible", 0),
            ("Kia", "Rio", 2023, 12500000, 12000, Transmision.MANUAL, Condicion.USADO, "reservado", 1),
        ]
        for marca, modelo, anio, precio, kilometraje, transmision, condicion, estado, sucursal in datos:
            session.add(Vehiculo(marca=marca, modelo=modelo, anio=anio, precio=precio,
                                 kilometraje=kilometraje, transmision=transmision.value,
                                 condicion=condicion.value, estado=estado,
                                 sucursal=sucursales[sucursal]))
        session.flush()
        vehiculo = session.query(Vehiculo).filter_by(modelo="Rio").one()
        session.add_all([
            Reserva(cliente=cliente, vehiculo=session.query(Vehiculo).filter_by(modelo="Tucson").one(),
                    fecha_reserva=date.today() - timedelta(days=20),
                    fecha_vencimiento=date.today() - timedelta(days=10),
                    monto_reserva=200000, estado="cancelada"),
            Reserva(cliente=cliente, vehiculo=vehiculo, fecha_reserva=date.today(),
                    fecha_vencimiento=date.today() + timedelta(days=7),
                    monto_reserva=150000, estado="activa"),
        ])
