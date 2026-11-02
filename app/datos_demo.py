"""Carga opcional de datos ficticios mediante ORM.

Ejecutar desde la raíz del proyecto:
    python -m app.datos_demo
"""

from datetime import date, timedelta

from app.db import SessionLocal
from app.domain.vehiculo import Condicion, Transmision
from app.models import Cliente, Reserva, Sucursal, Vehiculo


def cargar_datos_demo() -> None:
    """Carga datos ficticios solo cuando las cuatro tablas están vacías."""
    with SessionLocal.begin() as session:
        entidades = (Sucursal, Cliente, Vehiculo, Reserva)

        if any(session.query(entidad).first() for entidad in entidades):
            raise RuntimeError(
                "Los datos demo requieren una base de datos completamente vacía."
            )

        sucursales = [
            Sucursal(
                nombre="Sucursal Centro",
                direccion="Avenida Ficticia 100",
                ciudad="Temuco",
                telefono="56900000001",
                horario_atencion="Lunes a viernes 09:00-18:00",
            ),
            Sucursal(
                nombre="Sucursal Sur",
                direccion="Calle Ejemplo 200",
                ciudad="Valdivia",
                telefono="56900000002",
                horario_atencion="Lunes a viernes 09:00-18:00",
            ),
        ]
        session.add_all(sucursales)

        clientes = [
            Cliente(
                rut="00000000-0",
                nombre="Cliente Ficticio Uno",
                correo="cliente.uno@example.com",
                telefono="56900000003",
                direccion="Pasaje Inventado 30",
            ),
            Cliente(
                rut="11111111-1",
                nombre="Cliente Ficticio Dos",
                correo="cliente.dos@example.com",
                telefono="56900000004",
                direccion="Calle Imaginaria 40",
            ),
        ]
        session.add_all(clientes)
        session.flush()

        datos_vehiculos = [
            (
                "Toyota",
                "Yaris",
                2022,
                10990000,
                23000,
                Transmision.MANUAL,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Hyundai",
                "Tucson",
                2021,
                17990000,
                48000,
                Transmision.AUTOMATICA,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Kia",
                "Rio",
                2023,
                12500000,
                12000,
                Transmision.MANUAL,
                Condicion.USADO,
                "reservado",
                1,
            ),
            (
                "Mazda",
                "CX-5",
                2022,
                18990000,
                35000,
                Transmision.AUTOMATICA,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Nissan",
                "Versa",
                2023,
                12990000,
                18000,
                Transmision.MANUAL,
                Condicion.USADO,
                "disponible",
                1,
            ),
            (
                "Suzuki",
                "Swift",
                2024,
                11990000,
                9000,
                Transmision.MANUAL,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Chevrolet",
                "Onix",
                2022,
                10490000,
                41000,
                Transmision.MANUAL,
                Condicion.USADO,
                "disponible",
                1,
            ),
            (
                "Volkswagen",
                "Polo",
                2023,
                13990000,
                22000,
                Transmision.AUTOMATICA,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Peugeot",
                "208",
                2024,
                15990000,
                12000,
                Transmision.AUTOMATICA,
                Condicion.USADO,
                "disponible",
                1,
            ),
            (
                "Ford",
                "Ranger",
                2021,
                23990000,
                58000,
                Transmision.MANUAL,
                Condicion.USADO,
                "disponible",
                0,
            ),
            (
                "Honda",
                "Civic",
                2023,
                20990000,
                16000,
                Transmision.AUTOMATICA,
                Condicion.USADO,
                "disponible",
                1,
            ),
        ]

        for (
            marca,
            modelo,
            anio,
            precio,
            kilometraje,
            transmision,
            condicion,
            estado,
            indice_sucursal,
        ) in datos_vehiculos:
            session.add(
                Vehiculo(
                    marca=marca,
                    modelo=modelo,
                    anio=anio,
                    precio=precio,
                    kilometraje=kilometraje,
                    transmision=transmision.value,
                    condicion=condicion.value,
                    estado=estado,
                    sucursal=sucursales[indice_sucursal],
                )
            )

        session.flush()

        tucson = session.query(Vehiculo).filter_by(modelo="Tucson").one()
        rio = session.query(Vehiculo).filter_by(modelo="Rio").one()

        session.add_all(
            [
                Reserva(
                    cliente=clientes[0],
                    vehiculo=tucson,
                    fecha_reserva=date.today() - timedelta(days=20),
                    fecha_vencimiento=date.today() - timedelta(days=10),
                    monto_reserva=200000,
                    estado="cancelada",
                ),
                Reserva(
                    cliente=clientes[1],
                    vehiculo=rio,
                    fecha_reserva=date.today(),
                    fecha_vencimiento=date.today() + timedelta(days=7),
                    monto_reserva=150000,
                    estado="activa",
                ),
            ]
        )


if __name__ == "__main__":
    cargar_datos_demo()
    print("Datos demo cargados correctamente.")
