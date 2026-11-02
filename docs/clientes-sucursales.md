# Módulos de clientes y sucursales

## Alcance

Esta parte implementa las operaciones de creación, listado y consulta por ID para clientes y sucursales.

No incluye actualización ni eliminación.

## Endpoints

| Método | Ruta | Respuesta exitosa |
|---|---|---|
| POST | `/clientes` | `201 Created` |
| GET | `/clientes` | `200 OK` |
| GET | `/clientes/{id}` | `200 OK` |
| POST | `/sucursales` | `201 Created` |
| GET | `/sucursales` | `200 OK` |
| GET | `/sucursales/{id}` | `200 OK` |

## Datos de clientes

La creación recibe los siguientes campos obligatorios:

- `rut`: texto de al menos 1 carácter.
- `nombre`: texto de al menos 1 carácter.
- `correo`: texto de al menos 1 carácter.
- `telefono`: texto de al menos 1 carácter.
- `direccion`: texto de al menos 1 carácter.

Todos los campos deben recibirse como texto. No se aceptan campos adicionales.

El servidor asigna el ID al crear el cliente.

El RUT se normaliza eliminando puntos y espacios, y convirtiendo las letras a mayúsculas. No se permite registrar dos clientes con el mismo RUT normalizado.

Actualmente, el campo `correo` no realiza una validación de formato de dirección de correo electrónico; solamente comprueba que no esté vacío.

## Datos de sucursales

La creación recibe los siguientes campos obligatorios:

- `nombre`: texto de 2 a 100 caracteres.
- `direccion`: texto de 1 a 200 caracteres.
- `ciudad`: texto de 2 a 100 caracteres.
- `telefono`: texto de 1 a 30 caracteres.
- `horario_atencion`: texto de 1 a 120 caracteres.

El servidor asigna el ID al crear la sucursal. No se aceptan campos adicionales.

## Errores

- `404 RESOURCE_NOT_FOUND`: no existe el cliente o la sucursal solicitado.
- `409 DUPLICATE_RESOURCE`: ya existe un cliente con el RUT normalizado.
- `422 VALIDATION_ERROR`: los datos o parámetros no cumplen las validaciones del esquema.

Los errores utilizan el formato común de respuestas de error definido para la API.

## Ejecución

Desde la raíz del repositorio y con el entorno virtual activado, ejecutar:

```bash
uvicorn app.main:app --reload
```

La documentación interactiva de los endpoints está disponible en:

```text
http://127.0.0.1:8000/docs
```