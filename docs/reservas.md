# Modulo de reservas

Este modulo implementa las rutas de reservas sobre SQLAlchemy. Las reglas de
negocio se coordinan en el [servicio](../app/services/reservas.py) y las
consultas ORM viven en el [repositorio](../app/repositories/reservas.py).
El contrato compartido esta en [CONTRATO.md](../CONTRATO.md).

## Rutas y datos

| Metodo y ruta | Exito | Funcion |
| --- | --- | --- |
| `POST /reservas` | 201 | Crear una reserva activa |
| `GET /reservas` | 200 | Listar por ID ascendente |
| `GET /reservas/{id}` | 200 | Consultar una reserva |
| `PATCH /reservas/{id}` | 200 | Cancelar una reserva activa |

El cuerpo de creacion acepta `cliente_id`, `vehiculo_id`,
`fecha_vencimiento` y `monto_reserva`. El servidor asigna `id`,
`fecha_reserva` y `estado=activa`. El DTO rechaza campos adicionales, valores
nulos, IDs y montos no enteros o no positivos, y fechas que no sean validas.
`fecha_vencimiento` puede ser hoy, pero no una fecha anterior; la fecha pasada
es una regla de negocio 400, no una validacion de formato 422.

Ejemplo de creacion; la fecha debe actualizarse al ejecutar:

```json
{
  "cliente_id": 1,
  "vehiculo_id": 1,
  "fecha_vencimiento": "<hoy o una fecha futura en AAAA-MM-DD>",
  "monto_reserva": 500000
}
```

PATCH solo acepta `{"estado":"cancelada"}`. No se pueden establecer
manualmente los estados `activa` o `vencida`.

Estados:

- Reserva: `activa`, `cancelada`, `vencida`.
- Vehiculo: `disponible`, `reservado`, `vendido`; el servicio de reservas
  gestiona reservar y liberar. Los vehiculos vendidos no se liberan.

## Reglas y errores

- Cliente y vehiculo deben existir; si no, se responde 404.
- El vehiculo debe estar disponible y sin otra reserva activa; el conflicto
  responde 409 (`VEHICLE_NOT_AVAILABLE`).
- Solo se cancela una reserva activa. Cancelar cambia la reserva a
  `cancelada` y libera el vehiculo si no queda otra reserva activa.
- Una reserva vence cuando `fecha_vencimiento < date.today()`. La fecha igual
  a hoy sigue activa. Vencerla actualiza reserva y disponibilidad; un vehiculo
  vendido u ocupado por otra reserva activa valida no se libera.
- Al vencer o cancelar, el vehiculo puede reservarse nuevamente si queda
  disponible.
- Los errores controlados usan
  `{"error":{"code":"...","message":"...","details":[]}}`: 400 para reglas de
  negocio, 404 para recursos inexistentes, 409 para conflictos de estado y
  422 para DTO o parametros invalidos.

## Vencimientos y transacciones

`procesar_vencimientos_en_sesion(session, hoy=None)` permite que otro caso de
uso procese vencimientos dentro de su sesion SQLAlchemy. Devuelve la cantidad
de reservas vencidas y no hace commit ni abre otra sesion. El llamador es
responsable de confirmar o revertir la transaccion.

Ejemplo para integrar desde el servicio de vehiculos, antes de consultar o
cambiar disponibilidad:

```python
from app.db import SessionLocal
from app.services.reservas import procesar_vencimientos_en_sesion

with SessionLocal.begin() as session:
    procesar_vencimientos_en_sesion(session)
    # Consultar o modificar vehiculos usando esta misma session.
```

El contexto `SessionLocal.begin()` confirma al salir correctamente y revierte
si ocurre una excepcion. No se debe llamar a
`procesar_vencimientos(hoy=None)` desde una transaccion ya abierta: ese
adaptador de conveniencia abre y confirma su propia sesion.

`POST /reservas`, `GET /reservas`, `GET /reservas/{id}` y
`PATCH /reservas/{id}` procesan vencimientos antes de continuar. La creacion,
el cambio de estado de reserva y la actualizacion del vehiculo usan una sola
sesion y transaccion. Si una regla posterior falla, tambien se revierten los
cambios de vencimientos hechos por esa operacion. Por ejemplo, un intento de
crear con cliente inexistente devuelve 404 y deja sin cambios una reserva que
se habia procesado como vencida dentro de esa misma transaccion. Un GET de
lista exitoso confirma los vencimientos; un GET por ID inexistente devuelve
404 y revierte el procesamiento de esa llamada.

## Ejecucion y pruebas

Desde PowerShell, en la raiz del proyecto:

```powershell
.\.venv\Scripts\alembic.exe upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Las pruebas propias crean una SQLite temporal con fixtures ORM, migran antes
de insertar y pasan la misma URL al servidor de prueba:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_orm_integracion tests.test_reservas
```

Para requests manuales aislados, iniciar una base desechable y cargar los
datos demo opcionales:

```powershell
$env:CONCESIONARIA_DATABASE_URL = "sqlite:///./reservas-manual.db"
.\.venv\Scripts\alembic.exe upgrade head
$env:CONCESIONARIA_DATOS_DEMO = "1"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

El archivo [reservas.http](../tests_manual/reservas.http) usa el cliente 1 y
el vehiculo disponible 1 de esos datos demo. La fecha se genera en formato
local `AAAA-MM-DD`; el ID de la reserva debe copiarse de la respuesta POST si
no es el indicado en el archivo. Detener la API antes de eliminar
`reservas-manual.db`. No usar este procedimiento sobre una base con datos que
se quieran conservar.
