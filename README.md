# API de concesionaria

Proyecto academico de Desarrollo de Backend. La API registra sucursales,
clientes, vehiculos y reservas para consultar disponibilidad. Los datos
persisten en SQLite mediante SQLAlchemy y Alembic prepara el esquema.

## Estado y requisitos

La API integrada tiene los 15 endpoints de negocio acordados y `GET /health`.
Las cuatro entidades se guardan mediante ORM; los campos, estados y errores
estan en [CONTRATO.md](CONTRATO.md).

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

Se crean dos sucursales, dos clientes, once vehiculos y dos reservas. Una
reserva esta cancelada y otra activa. La carga exige una base completamente
vacia y no borra datos. Para reiniciar el proceso conservando lo guardado,
detiene Uvicorn, quita la variable y vuelve a iniciarlo:

```powershell
Remove-Item Env:CONCESIONARIA_DATOS_DEMO
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Los ejemplos cumplen el minimo de dos registros por entidad y no sustituyen
las fixtures de pruebas.

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

Los servicios de clientes y sucursales delegan sus consultas ORM a sus
repositorios. Vehiculos llama a `procesar_vencimientos_en_sesion(session)`
antes de consultar o modificar disponibilidad; el vencimiento y la operacion
comparten la transaccion, de modo que un error revierte ambos cambios.

Las relaciones son sucursal 1:N vehiculos, cliente 1:N reservas y vehiculo
1:N reservas historicas. SQLite comprueba claves foraneas por conexion. La
nueva migracion impide reutilizar IDs eliminados desde que se aplica; una
base antigua no conserva informacion sobre IDs borrados antes de migrarla.

## Pruebas y evidencias

Las pruebas preparan SQLite temporal, aplican Alembic, crean fixtures ORM y
pasan la misma URL a sus procesos HTTP. Para ejecutar la suite completa:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Cubren CRUD, validaciones, reglas, filtros, orden, paginacion, vencimientos,
claves foraneas, migracion, no reutilizacion de IDs y persistencia tras
reiniciar Uvicorn. `limpiar_base()` se usa solo sobre bases temporales de
prueba; no lo ejecutes sobre `concesionaria.db` ni sobre una API en uso.
Los diagramas estan en [docs/diagramas.md](docs/diagramas.md) y los casos
reproducibles en [docs/evidencias-pruebas.md](docs/evidencias-pruebas.md).
La presentacion del proyecto es el 2 de noviembre de 2026 a las 10:05.
