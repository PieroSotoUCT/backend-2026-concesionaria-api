# Contrato compartido de la API

Este documento coordina el trabajo de los tres integrantes. La entrega final
del grupo tendra 15 endpoints de negocio; en esta sesion se implementan solo
vehiculos y la base comun. Los otros modulos siguen a cargo de sus responsables.

## Reparto

| Responsable | Modulo | Seguimiento principal |
| --- | --- | --- |
| Yo | Base compartida y vehiculos | Coordinacion, API e integracion |
| Companero 1 | Clientes y sucursales | Dominio, datos y documentacion |
| Companero 2 | Reservas | Calidad y pruebas del conjunto |

Los nombres reales y la autorizacion docente para un grupo de tres estan
pendientes. La guia describe grupos de cuatro o cinco.

## Almacenamiento y campos

`app/repositories/datos.py` contiene los cuatro diccionarios compartidos.
Cada clave es un ID entero; cada valor es un diccionario con los campos de la
tabla. `siguiente_id(nombre_coleccion)` aumenta el contador correspondiente.
Los IDs eliminados no se reutilizan. Las fechas se guardan como `date` de
Python, los montos como enteros en pesos chilenos y los estados como texto.
Se usa la fecha local de la maquina que ejecuta la API (`date.today()`) en
todas las operaciones que dependen de hoy. La demostracion debe ejecutarse
con el reloj y la zona horaria local configurados correctamente.

| Coleccion | Campos del registro |
| --- | --- |
| `sucursales` | `id`, `nombre`, `direccion`, `ciudad`, `telefono`, `horario_atencion` |
| `vehiculos` | `id`, `marca`, `modelo`, `anio`, `precio`, `kilometraje`, `transmision`, `condicion`, `estado`, `sucursal_id` |
| `clientes` | `id`, `rut`, `nombre`, `correo`, `telefono`, `direccion` |
| `reservas` | `id`, `cliente_id`, `vehiculo_id`, `fecha_reserva`, `fecha_vencimiento`, `monto_reserva`, `estado` |

Estados: vehiculo `disponible`, `reservado`, `vendido`; reserva `activa`,
`cancelada`, `vencida`; condicion `nuevo`, `usado`; transmision `manual`,
`automatica`. Sucursal 1:N vehiculos; cliente 1:N reservas; vehiculo 1:N
reservas historicas. Las funciones de cada repositorio leen y escriben las
mismas colecciones: no hay copias por modulo.

## Rutas acordadas

| Responsable | Metodo y ruta | Proposito |
| --- | --- | --- |
| Vehiculos | `POST /vehiculos` | Crear un vehiculo en una sucursal existente |
| Vehiculos | `GET /vehiculos` | Listar con filtros, orden y paginacion |
| Vehiculos | `GET /vehiculos/{id}` | Obtener uno |
| Vehiculos | `PATCH /vehiculos/{id}` | Actualizar campos enviados |
| Vehiculos | `DELETE /vehiculos/{id}` | Eliminar si no tiene reservas historicas |
| Sucursales | `POST /sucursales` | Crear |
| Sucursales | `GET /sucursales` | Listar |
| Sucursales | `GET /sucursales/{id}` | Obtener una |
| Clientes | `POST /clientes` | Crear, con RUT normalizado unico |
| Clientes | `GET /clientes` | Listar |
| Clientes | `GET /clientes/{id}` | Obtener uno |
| Reservas | `POST /reservas` | Reservar vehiculo disponible |
| Reservas | `GET /reservas` | Listar |
| Reservas | `GET /reservas/{id}` | Obtener una |
| Reservas | `PATCH /reservas/{id}` | Aceptar solo `{"estado":"cancelada"}` |

`POST` responde 201; consultas y `PATCH`, 200; `DELETE`, 204 sin cuerpo.
Los DTO de creacion no aceptan IDs ni estados asignados por el servidor.
`PATCH` solo cambia campos presentes y rechaza `null` para campos obligatorios.
En vehiculos, el estado `reservado` pertenece al servicio de reservas; la
unica transicion manual permitida es de `disponible` a `vendido`. `vendido`
es final. Crear o modificar un vehiculo exige `sucursal_id` existente.
Eliminarlo exige que no haya ninguna reserva que lo mencione.

## Consulta de vehiculos

`GET /vehiculos` admite `marca`, `estado`, `sucursal_id`, `precio_min`,
`precio_max`; `ordenar_por=precio|anio|kilometraje` y
`direccion=asc|desc`; `pagina` desde 1 y `limite` entre 1 y 100.
Por defecto: `pagina=1`, `limite=10`; sin `ordenar_por`, ID ascendente.
La marca se compara sin distinguir mayusculas y despues de quitar espacios
de los extremos. Se aplican filtros, luego orden y finalmente paginacion.
`precio_min` no puede superar `precio_max`.

La respuesta tiene `items`, `total`, `pagina`, `limite`, `total_paginas`.
`total` se calcula antes de paginar. Sin resultados, `items=[]` y
`total_paginas=0`; una pagina superior al final tambien devuelve `items=[]`
sin alterar los totales.

## Errores y validaciones

Todos los errores controlados usan este formato, incluida la validacion 422:

```json
{"error":{"code":"RESOURCE_NOT_FOUND","message":"Descripcion clara","details":[]}}
```

Se usa 400 para reglas de negocio, 404 para recursos inexistentes, 409 para
duplicados o conflictos de estado, y 422 para datos o parametros invalidos.
El modulo compartido `app/errores.py` define `ErrorAplicacion` para las
operaciones de negocio. Los errores inesperados conservan el manejo normal
de FastAPI; no se disfrazan como 400.

Las validaciones de datos incluyen longitudes, rangos numericos, valores
enumerados y formatos. Las reglas de negocio incluyen sucursal existente,
ausencia de reservas antes de eliminar, transiciones de estado, cliente y
vehiculo existentes al reservar, y RUT unico. Cada equipo documentara sus
ejemplos y pruebas. La normalizacion del RUT quita puntos y espacios y pasa
letras a mayusculas; no incluye comprobacion del digito verificador.

## Conexion de modulos

La API registra solo routers existentes. Vehiculos consulta sucursales y
reservas directamente mediante funciones pequenas de su repositorio y las
colecciones comunes. El modulo de reservas implementara la revision de
vencimientos: una reserva vence cuando `fecha_vencimiento < date.today()`.
Al integrarlo, se llamara antes de consultas y operaciones que afecten
disponibilidad. Hasta entonces, las pruebas aisladas de vehiculos usan datos
de demostracion coherentes y dejan esa conexion marcada como pendiente.
