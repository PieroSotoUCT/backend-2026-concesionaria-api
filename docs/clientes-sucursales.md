# Módulos de clientes y sucursales

## 1. Alcance

Esta parte implementa los módulos de clientes y sucursales de la API de la concesionaria.

Cada módulo contempla las siguientes operaciones:

- Creación de registros.
- Listado de registros.
- Consulta de registros por ID.

La implementación utiliza SQLAlchemy ORM para la persistencia de información en la base de datos.

No se incluyen operaciones de actualización ni eliminación para estos módulos.

## 2. Arquitectura e implementación

Los módulos siguen una separación por responsabilidades:

- **Entidades y modelos ORM:** representan los datos y su estructura en la base de datos.
- **Esquemas (DTO):** definen los datos de entrada y salida, junto con sus validaciones.
- **Repositorios:** encapsulan las operaciones de acceso a los datos.
- **Servicios:** implementan las reglas de negocio y gestionan las operaciones transaccionales.
- **Routers:** exponen los endpoints HTTP mediante FastAPI.

La persistencia se realiza utilizando sesiones SQLAlchemy y las operaciones de escritura se ejecutan mediante transacciones.

## 3. Endpoints

### Clientes

| Método | Ruta | Respuesta exitosa |
|---|---|---|
| POST | `/clientes` | `201 Created` |
| GET | `/clientes` | `200 OK` |
| GET | `/clientes/{id}` | `200 OK` |

### Sucursales

| Método | Ruta | Respuesta exitosa |
|---|---|---|
| POST | `/sucursales` | `201 Created` |
| GET | `/sucursales` | `200 OK` |
| GET | `/sucursales/{id}` | `200 OK` |

## 4. Datos y validaciones de clientes

La creación de clientes utiliza el esquema `ClienteCrear`, que recibe los siguientes campos obligatorios:

| Campo | Tipo | Restricciones |
|---|---|---|
| `rut` | Texto | 3 a 20 caracteres |
| `nombre` | Texto | 2 a 100 caracteres |
| `correo` | Email | Dirección de correo válida |
| `telefono` | Texto | 1 a 30 caracteres |
| `direccion` | Texto | 1 a 200 caracteres |

### Reglas de validación

- Todos los campos son obligatorios.
- No se aceptan campos adicionales (`extra="forbid"`).
- Se eliminan los espacios exteriores de los campos de texto mediante `str_strip_whitespace=True`.
- Los valores que quedan vacíos después de eliminar los espacios son rechazados por las restricciones de longitud.
- El correo electrónico se valida mediante `EmailStr`.
- El identificador es asignado por el servidor al registrar el cliente.

### Normalización y unicidad del RUT

Antes de registrar un cliente, el servicio normaliza su RUT mediante las siguientes operaciones:

1. Elimina los puntos.
2. Elimina los espacios.
3. Convierte las letras a mayúsculas.

Por ejemplo:

`12.345.678-k` se convierte en `12345678-K`.

No se permite registrar dos clientes con el mismo RUT normalizado.

La unicidad se controla mediante una consulta al repositorio y también mediante una restricción `UNIQUE` en la base de datos.

Cuando se detecta un RUT duplicado, el servicio devuelve un error HTTP `409` con el código `DUPLICATE_RESOURCE`.

También se contempla la captura de conflictos de integridad de SQLite asociados específicamente a la unicidad del RUT.

## 5. Datos y validaciones de sucursales

La creación de sucursales utiliza el esquema `SucursalCrear`.

Los campos obligatorios son:

| Campo | Tipo | Restricciones |
|---|---|---|
| `nombre` | Texto | 2 a 100 caracteres |
| `direccion` | Texto | 1 a 200 caracteres |
| `ciudad` | Texto | 2 a 100 caracteres |
| `telefono` | Texto | 1 a 30 caracteres |
| `horario_atencion` | Texto | 1 a 120 caracteres |

### Reglas de validación

- Todos los campos son obligatorios.
- No se aceptan campos adicionales (`extra="forbid"`).
- Se eliminan los espacios exteriores de los campos de texto mediante `str_strip_whitespace=True`.
- Los campos vacíos después de la normalización son rechazados.
- El identificador es asignado por el servidor.

## 6. Persistencia y transacciones

Los módulos utilizan modelos ORM para almacenar y recuperar información de la base de datos.

Las operaciones de escritura se ejecutan dentro de transacciones administradas por SQLAlchemy.

Esto permite mantener la integridad de los registros y realizar rollback cuando ocurre un error durante una operación transaccional.

La restricción de unicidad del RUT se encuentra respaldada por la base de datos, evitando duplicados incluso ante solicitudes concurrentes.

## 7. Manejo de errores HTTP

Los errores de la API utilizan el formato común definido para el proyecto:

- `404 RESOURCE_NOT_FOUND`: el cliente o la sucursal solicitada no existe.
- `409 DUPLICATE_RESOURCE`: ya existe un cliente con el RUT normalizado.
- `422 VALIDATION_ERROR`: los datos enviados o parámetros de entrada no cumplen las validaciones del esquema.

Las respuestas de error mantienen una estructura común:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "El recurso no existe",
    "details": []
  }
}
```

Los errores son gestionados mediante el mecanismo común de excepciones de la aplicación.

## 8. Pruebas automatizadas

Se implementaron pruebas unitarias para verificar las reglas de negocio y los endpoints HTTP de ambos módulos.

### Clientes

Las pruebas contemplan:

- Creación de clientes.
- Normalización del RUT.
- Listado de clientes.
- Consulta de clientes existentes.
- Respuesta `404` para clientes inexistentes.
- Respuesta `409` para RUT duplicados.
- Validación de correos electrónicos.
- Rechazo de datos obligatorios faltantes.
- Distinción entre conflictos de unicidad del RUT y otros errores de integridad.

### Sucursales

Se realizaron pruebas para verificar las operaciones de creación, listado y consulta, además de las validaciones correspondientes al esquema.

### Resultado

**14 pruebas automatizadas aprobadas:**

- Clientes: 9 pruebas.
- Sucursales: 5 pruebas.

Comando utilizado:

```bash
python -m unittest tests.test_clientes tests.test_sucursales -v
```

## 9. Pruebas HTTP manuales

Se dispone del archivo:

`tests_manual/clientes_sucursales.http`

Este archivo contiene solicitudes para comprobar:

- Listado de clientes y sucursales.
- Creación de clientes y sucursales.
- Consulta de recursos existentes.
- Consulta de recursos inexistentes.
- RUT duplicados.
- Correos electrónicos inválidos.
- Campos adicionales no permitidos.
- Datos compuestos únicamente por espacios.

Las solicitudes están preparadas para ejecutarse mediante la extensión REST Client de Visual Studio Code.

## 10. Calidad del código

Se ejecutaron las siguientes verificaciones sobre los archivos correspondientes a los módulos:

```bash
python -m ruff check \
app/datos_demo.py \
app/repositories/clientes.py \
app/repositories/sucursales.py \
app/routers/clientes.py \
app/routers/sucursales.py \
app/schemas/clientes.py \
app/schemas/sucursal.py \
app/services/clientes.py \
app/services/sucursales.py \
tests/test_clientes.py \
tests/test_sucursales.py
```

**Resultado:** `All checks passed!`

También se ejecutó `git diff --check` sin observaciones en la revisión anterior.

## 11. Datos de demostración

El proyecto incorpora un mecanismo de carga explícita de datos ficticios mediante ORM.

Su ejecución se realiza desde la raíz del repositorio:

```bash
python -m app.datos_demo
```

El seeder verifica que las tablas estén vacías antes de insertar registros, evitando duplicaciones y modificaciones accidentales de datos existentes.

En una base de datos limpia, la carga verificada contempla:

| Entidad | Registros |
|---|---:|
| Clientes | 2 |
| Sucursales | 2 |
| Vehículos | 11 |
| Reservas | 2 |

La prueba aislada confirmó que los 11 vehículos tienen una sucursal válida y que las 2 reservas tienen clientes y vehículos asociados correctamente.

## 12. Ejecución del proyecto

Desde la raíz del repositorio y con el entorno virtual activado, iniciar la aplicación mediante:

```bash
uvicorn app.main:app --reload
```

La documentación interactiva de los endpoints está disponible en:

```text
http://127.0.0.1:8000/docs
```

La configuración de conexión a la base de datos se administra mediante `CONCESIONARIA_DATABASE_URL`.