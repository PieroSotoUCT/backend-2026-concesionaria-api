"""Carga opcional de datos ficticios para probar el modulo de vehiculos."""

from datetime import date, timedelta

from app.domain.vehiculo import Condicion, EstadoVehiculo, Transmision, Vehiculo
from app.repositories.datos import (
    clientes,
    contadores,
    reservas,
    siguiente_id,
    sucursales,
    vehiculos,
)


def cargar_datos_demo() -> None:
    """Carga ejemplos una vez, solo cuando el almacenamiento esta vacio."""
    if any((sucursales, vehiculos, clientes, reservas)) or any(contadores.values()):
        raise RuntimeError("Los datos demo requieren iniciar con memoria vacia")

    for nombre, direccion, ciudad, telefono in (
        ("Sucursal Centro", "Avenida Ficticia 100", "Temuco", "56900000001"),
        ("Sucursal Sur", "Calle Ejemplo 200", "Valdivia", "56900000002"),
    ):
        sucursal_id = siguiente_id("sucursales")
        sucursales[sucursal_id] = {
            "id": sucursal_id,
            "nombre": nombre,
            "direccion": direccion,
            "ciudad": ciudad,
            "telefono": telefono,
            "horario_atencion": "Lunes a viernes 09:00-18:00",
        }

    cliente_id = siguiente_id("clientes")
    clientes[cliente_id] = {
        "id": cliente_id,
        "rut": "00000000-0",
        "nombre": "Cliente Ficticio",
        "correo": "cliente.demo@example.com",
        "telefono": "56900000003",
        "direccion": "Pasaje Inventado 30",
    }

    ejemplos_vehiculos = [
        {"marca": "Toyota", "modelo": "Yaris", "anio": 2022, "precio": 10990000,
         "kilometraje": 23000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Hyundai", "modelo": "Tucson", "anio": 2021, "precio": 17990000,
         "kilometraje": 48000, "transmision": Transmision.AUTOMATICA,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Kia", "modelo": "Rio", "anio": 2023, "precio": 12500000,
         "kilometraje": 12000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.RESERVADO,
         "sucursal_id": 2},
        {"marca": "Suzuki", "modelo": "Swift", "anio": 2024, "precio": 14900000,
         "kilometraje": 0, "transmision": Transmision.MANUAL,
         "condicion": Condicion.NUEVO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Mazda", "modelo": "3 Sedan", "anio": 2020, "precio": 13900000,
         "kilometraje": 61000, "transmision": Transmision.AUTOMATICA,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 2},
        {"marca": "Toyota", "modelo": "Corolla", "anio": 2025, "precio": 20990000,
         "kilometraje": 0, "transmision": Transmision.AUTOMATICA,
         "condicion": Condicion.NUEVO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 2},
        {"marca": "Nissan", "modelo": "Versa", "anio": 2022, "precio": 11900000,
         "kilometraje": 36000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Ford", "modelo": "Ranger", "anio": 2024, "precio": 31900000,
         "kilometraje": 8000, "transmision": Transmision.AUTOMATICA,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.VENDIDO,
         "sucursal_id": 2},
        {"marca": "Toyota", "modelo": "Hilux", "anio": 2021, "precio": 24900000,
         "kilometraje": 75000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Chevrolet", "modelo": "Onix", "anio": 2023, "precio": 12900000,
         "kilometraje": 18000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 2},
        {"marca": "Hyundai", "modelo": "Accent", "anio": 2019, "precio": 8900000,
         "kilometraje": 95000, "transmision": Transmision.MANUAL,
         "condicion": Condicion.USADO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 1},
        {"marca": "Mazda", "modelo": "CX-5", "anio": 2025, "precio": 28900000,
         "kilometraje": 0, "transmision": Transmision.AUTOMATICA,
         "condicion": Condicion.NUEVO, "estado": EstadoVehiculo.DISPONIBLE,
         "sucursal_id": 2},
    ]
    for ejemplo in ejemplos_vehiculos:
        vehiculo = Vehiculo(id=siguiente_id("vehiculos"), **ejemplo)
        vehiculos[vehiculo.id] = vehiculo.a_registro()

    hoy = date.today()
    ejemplos_reservas = [
        {
            "vehiculo_id": 2,
            "fecha_reserva": hoy - timedelta(days=20),
            "fecha_vencimiento": hoy - timedelta(days=10),
            "monto_reserva": 200000,
            "estado": "cancelada",
        },
        {
            "vehiculo_id": 3,
            "fecha_reserva": hoy,
            "fecha_vencimiento": hoy + timedelta(days=7),
            "monto_reserva": 150000,
            "estado": "activa",
        },
    ]
    for ejemplo in ejemplos_reservas:
        reserva_id = siguiente_id("reservas")
        reservas[reserva_id] = {
            "id": reserva_id,
            "cliente_id": cliente_id,
            **ejemplo,
        }
