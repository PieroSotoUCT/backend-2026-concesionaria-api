# API de concesionaria

Proyecto academico de Desarrollo de Backend. La API registra sucursales,
clientes, vehiculos y reservas para consultar disponibilidad. Los datos
persisten en SQLite mediante SQLAlchemy y Alembic prepara el esquema.

## Estado y requisitos

`main` ya incorporo los PR #1 (vehiculos), #2 (reservas), #3 (clientes y
sucursales) y #4 (ORM). Tiene los 15 endpoints de negocio acordados y
`GET /health`. La rama `fix/base-vehiculos-integracion` prepara correcciones
de base y vehiculos pendientes de integrar. Campos, estados y errores estan
en [CONTRATO.md](CONTRATO.md).

## Instalacion y configuracion en PowerShell

Desde la raiz del repositorio, con Python 3.10 o posterior:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

API y Alembic usan por defecto `sqlite:///./concesionaria.db`. Para elegir
otra base, define la URL **antes** de migrar e iniciar:

```powershell
$env:CONCESIONARIA_DATABASE_URL = "sqlite:///./concesionaria.db"
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

`.env.example` muestra la variable sin secretos; la aplicacion no carga
archivos `.env` automaticamente. Importar `app.main` no crea tablas. Para
preparar una copia limpia, ejecuta siempre `alembic upgrade head` antes de
iniciar. La revision nueva actualiza tambien una base de la revision anterior
sin borrar registros.

En otra ventana, `Invoke-RestMethod http://127.0.0.1:8000/health` responde
`{"estado":"ok"}`. Swagger esta en <http://127.0.0.1:8000/docs> y el JSON
OpenAPI en <http://127.0.0.1:8000/openapi.json>.

## Datos iniciales opcionales

En una **base vacia ya migrada**, activa los ejemplos ficticios al iniciar:

```powershell
$env:CONCESIONARIA_DATOS_DEMO = "1"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Se crean dos sucursales, un cliente, tres vehiculos y dos reservas. El
vehiculo 2 tiene una reserva cancelada y el 3 una activa. La carga exige base
vacia y no borra datos. Para reiniciar el proceso conservando lo guardado,
detiene Uvicorn, quita la variable y vuelve a iniciarlo:

```powershell
Remove-Item Env:CONCESIONARIA_DATOS_DEMO
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

El requisito academico pide dos registros por entidad. Falta un segundo
cliente en `app/datos_demo.py`, archivo a cargo de Gabriel. Los ejemplos no
sustituyen las fixtures de pruebas.

## Endpoints

| Modulo | Rutas | Responsable |
| --- | --- | --- |
| Vehiculos | `POST /vehiculos`, `GET /vehiculos`, `GET /vehiculos/{id}`, `PATCH /vehiculos/{id}`, `DELETE /vehiculos/{id}` | Piero |
| Sucursales | `POST /sucursales`, `GET /sucursales`, `GET /sucursales/{id}` | Gabriel |
| Clientes | `POST /clientes`, `GET /clientes`, `GET /clientes/{id}` | Gabriel |
| Reservas | `POST /reservas`, `GET /reservas`, `GET /reservas/{id}`, `PATCH /reservas/{id}` | Roberto |

`GET /health` no cuenta como endpoint de negocio. `POST` responde 201;
consultas y `PATCH`, 200; `DELETE /vehiculos/{id}`, 204 sin cuerpo. Los
errores controlados siguen
`{"error":{"code":"...","message":"...","details":[]}}`: 400 para
reglas, 404 para ausentes, 409 para conflictos y 422 para datos invalidos.

`GET /vehiculos` filtra por `marca`, `estado`, `sucursal_id`, `precio_min` y
`precio_max`; ordena por `precio`, `anio` o `kilometraje`; y pagina con
`pagina` y `limite`. El total se calcula despues de filtrar y antes de
paginar. Con la base demo nueva, esta consulta devuelve el vehiculo 1,
`total=1` y `total_paginas=1`:

```http
GET /vehiculos?marca=toyota&estado=disponible&sucursal_id=1&ordenar_por=precio&direccion=desc&pagina=1&limite=1
```

Para CRUD y errores manuales, sigue las 33 solicitudes de
[tests_manual/vehiculos.http](tests_manual/vehiculos.http) sobre la SQLite de
prueba nueva indicada en ese archivo.

## Capas y persistencia

Una solicitud de vehiculos recorre `app/routers/vehiculos.py` (HTTP),
`app/schemas/vehiculo.py` (DTO), `app/services/vehiculos.py` (reglas),
`app/repositories/vehiculos.py` (consultas ORM) y `app/models.py` con
`app/db.py` (persistencia). `_registro` en el servicio convierte el modelo
ORM a respuesta. `app/domain/vehiculo.py` define valores permitidos.
Reservas guarda la reserva y el estado del vehiculo en una transaccion propia.

Los servicios de clientes y sucursales aun hacen consultas ORM directamente;
Gabriel debe moverlas a sus repositorios. La funcion publica de vencimientos
de Roberto se ejecuta antes de consultas y cambios de vehiculos, pero abre
una transaccion separada; queda pendiente una interfaz con sesion compartida.

Las relaciones son sucursal 1:N vehiculos, cliente 1:N reservas y vehiculo
1:N reservas historicas. SQLite comprueba claves foraneas por conexion. La
nueva migracion impide reutilizar IDs eliminados desde que se aplica; una
base antigua no conserva informacion sobre IDs borrados antes de migrarla.

## Pruebas y evidencias

Las pruebas propias preparan SQLite temporal, aplican Alembic, crean
fixtures ORM y pasan la misma URL al proceso HTTP:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_base_piero tests.test_vehiculos tests.test_vehiculos_orm -v
```

Cubren CRUD, validaciones, reglas, filtros, orden, paginacion, vencimientos,
claves foraneas, migracion y no reutilizacion de IDs. No ejecutes
`limpiar_base()` sobre `concesionaria.db` ni sobre una API en uso. Las pruebas
de Gabriel y Roberto aun requieren fixtures ORM aisladas; sus fallos se
registran en [docs/avance-piero.md](docs/avance-piero.md).

Faltan el segundo cliente del seeder, los diagramas de clases y datos de
Gabriel, y las seis evidencias reproducibles de Roberto. La persistencia tras
reiniciar debe demostrarse con la misma base y sin recargar el seeder. El
numero de grupo, el nombre academico del repositorio y la autorizacion de
un equipo de tres requieren confirmacion docente.
