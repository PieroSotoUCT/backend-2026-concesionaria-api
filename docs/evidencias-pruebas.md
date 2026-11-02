# Evidencias de pruebas

## Entorno y comandos ejecutados

Las pruebas de reservas, clientes y sucursales usan una SQLite en la carpeta
temporal del sistema, con un nombre que incluye el PID del proceso. Configuran
`CONCESIONARIA_DATABASE_URL` antes de importar `app.db`, ejecutan
`alembic upgrade head` antes de insertar fixtures y heredan la misma URL en
los servidores Uvicorn de prueba. Al salir, eliminan solo el archivo temporal
creado por ese proceso y sus archivos auxiliares.

Comandos ejecutados desde la raiz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_orm_integracion tests.test_reservas
.\.venv\Scripts\python.exe -m unittest tests.test_reservas
.\.venv\Scripts\python.exe -m unittest tests.test_orm_integracion
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Resultados reales:

- Ambos modulos juntos: 20 pruebas, correcto.
- `test_reservas`: 17 pruebas, correcto.
- `test_orm_integracion`: 3 pruebas, correcto.
- Suite completa de integracion: 53 pruebas aprobadas en SQLite temporal.
- `compileall` para `app` y `tests`, y `git diff --check`: correctos en la
  revision individual anterior.

## Casos ejecutados

### RSV-CRUD-01 — Crear, consultar y cancelar una reserva

- **Requisito:** Crear devuelve 201; consultar y listar devuelven 200; PATCH
  cancela una reserva activa y libera el vehiculo.
- **Preparacion:** Migracion Alembic en SQLite temporal y fixture ORM con
  sucursal, cliente y vehiculos relacionados.
- **Entrada/comando:** Flujo HTTP probado por
  `PruebasReservasHTTP.test_flujo_completo_y_formato_de_errores`: POST,
  GET por ID, GET de lista y PATCH `{"estado":"cancelada"}`.
- **Esperado:** La reserva se crea activa, se puede recuperar, queda cancelada
  y el vehiculo puede reservarse nuevamente.
- **Obtenido:** Las respuestas y estados persistidos cumplieron las
  expectativas del test.
- **Estado:** Aprobado en pruebas propias. El contrato de reservas no define
  DELETE; el CRUD completo de vehiculos se comprueba en VEH-CRUD-01.

### RSV-INVALID-01 — Datos de entrada invalidos

- **Requisito:** Datos nulos, incompatibles, mal formados o campos adicionales
  producen 422 con el formato de error comun.
- **Preparacion:** Servidor de prueba con la misma SQLite temporal y cliente y
  vehiculos validos.
- **Entrada/comando:** Montos cero o como texto, IDs incompatibles, fecha mal
  formada, campos extra o nulos y estados PATCH no permitidos.
- **Esperado:** HTTP 422 y cuerpo `error.code=VALIDATION_ERROR`.
- **Obtenido:** Todos los casos ejercitados devolvieron 422 y el esquema
  esperado.
- **Estado:** Aprobado en `test_reservas`.

### RSV-404-01 — Referencias y reserva inexistentes

- **Requisito:** Cliente, vehiculo o reserva inexistente produce 404 sin
  escrituras parciales.
- **Preparacion:** Base temporal migrada con fixtures ORM completos; se usan
  IDs no existentes.
- **Entrada/comando:** Crear con cliente o vehiculo inexistente; consultar
  `/reservas/999` y PATCH de `/reservas/999`.
- **Esperado:** HTTP 404 y `error.code=RESOURCE_NOT_FOUND`.
- **Obtenido:** Los casos devolvieron 404; las pruebas de servicio verificaron
  que no se insertara una reserva al faltar una referencia.
- **Estado:** Aprobado en pruebas propias.

### RSV-RULE-01 — Doble reserva y segunda reserva tras liberar

- **Requisito:** Una reserva activa impide otra reserva del mismo vehiculo.
  Cancelar la reserva activa libera el vehiculo cuando corresponde.
- **Preparacion:** Vehiculo disponible, cliente valido y base temporal aislada.
- **Entrada/comando:** Crear dos veces para el mismo vehiculo; cancelar la
  primera y volver a crear.
- **Esperado:** El segundo intento simultaneo en secuencia responde 409; tras
  cancelar, una nueva reserva responde 201.
- **Obtenido:** Se verifico el conflicto, una sola reserva activa en otra
  sesion y la posibilidad de reservar nuevamente despues de cancelar.
- **Estado:** Aprobado en pruebas propias.

### RSV-EXP-01 — Limite, idempotencia y disponibilidad al vencer

- **Requisito:** La fecha igual a hoy sigue activa; una fecha anterior vence.
  No se libera un vehiculo vendido ni uno con otra reserva activa valida.
- **Preparacion:** Fixtures ORM con fechas relativas y vehiculos disponibles,
  reservados y vendidos.
- **Entrada/comando:** Procesar vencimientos para hoy y para el dia posterior
  al vencimiento; repetir el procesamiento.
- **Esperado:** Solo vencen reservas con `fecha_vencimiento < hoy`; el segundo
  procesamiento no repite cambios.
- **Obtenido:** El conteo fue 0 en el limite, 1 al vencer y 0 al repetir.
  Las comprobaciones ORM confirmaron que un vehiculo vendido se mantuvo
  vendido y que otro con reserva activa valida siguio reservado.
- **Estado:** Aprobado en pruebas propias.

### RSV-ROLLBACK-01 — Rollback despues de procesar vencimientos

- **Requisito:** Un error posterior a una escritura dentro de la transaccion
  no debe persistir cambios parciales.
- **Preparacion:** Reserva vencida aun activa y vehiculo reservado. La prueba
  usa una segunda sesion para observar el estado persistido.
- **Entrada/comando:** Intentar crear otra reserva con cliente inexistente.
  El servicio procesa y hace flush del vencimiento antes de validar el
  cliente; la validacion devuelve 404.
- **Esperado:** El error revierte el cambio de la reserva y del vehiculo.
- **Obtenido:** Tras el 404, otra sesion observo la reserva activa y el
  vehiculo reservado originales. Procesar vencimientos en una transaccion
  exitosa posterior si guardo la reserva vencida y libero el vehiculo.
- **Estado:** Aprobado en `test_error_despues_de_escrituras_revierten_la_transaccion`.

### RSV-PERSIST-01 — Persistencia tras reiniciar la API

- **Requisito:** Un proceso nuevo recupera datos confirmados sin seeder.
- **Preparacion:** SQLite temporal migrada y fixtures ORM; el entorno del
  proceso Uvicorn apunta a esa misma base y `CONCESIONARIA_DATOS_DEMO` esta
  desactivado.
- **Entrada/comando:** POST `/reservas`; detener Uvicorn; iniciar otro proceso
  con la misma URL y consultar GET `/reservas/{id}`.
- **Esperado:** El proceso nuevo recupera la misma reserva y el vehiculo
  permanece reservado.
- **Obtenido:** POST respondio 201; tras reiniciar, GET devolvio la reserva
  creada y una sesion independiente confirmo el estado reservado.
- **Estado:** Aprobado en `test_persistencia_tras_reiniciar_proceso_sin_seeder`.

## Casos de integracion comprobados

### VEH-CRUD-01 — CRUD completo de vehiculos

- **Requisito:** Crear, consultar, actualizar y eliminar segun las reglas del
  contrato.
- **Preparacion:** SQLite temporal migrada y fixtures ORM del modulo.
- **Entrada/comando:** `tests.test_vehiculos` y `tests.test_vehiculos_orm`:
  POST, GET, PATCH y DELETE `/vehiculos` con IDs obtenidos de las respuestas.
- **Esperado:** 201 al crear, 200 al consultar y actualizar, 204 al eliminar;
  no se reutiliza el ID eliminado.
- **Obtenido:** Las respuestas, estados y el ID nuevo cumplieron lo esperado.
- **Responsable/estado:** Piero; aprobado en la suite completa.

### VEH-QUERY-01 — Filtros, orden y paginacion

- **Requisito:** Verificar filtros, orden, desempate por ID, limites y
  metadatos de paginacion.
- **Preparacion:** SQLite temporal migrada con vehiculos de distintas marcas,
  sucursales, precios y estados.
- **Entrada/comando:** `GET /vehiculos` con marca, estado, sucursal, rango de
  precio, orden descendente, pagina y limite en `tests.test_vehiculos_orm`.
- **Esperado:** Filtrar, ordenar y paginar en ese orden; `total` anterior a la
  paginacion y desempate por ID.
- **Obtenido:** Los IDs y metadatos de ambas paginas coincidieron con lo
  esperado.
- **Responsable/estado:** Piero; aprobado en la suite completa.

### INT-CLIENTES-SUCURSALES-01 — Persistencia y reglas de clientes y sucursales

- **Requisito:** Verificar altas, consultas, referencias y validaciones de los
  modulos integrados.
- **Preparacion:** Motores SQLite temporales y fixtures ORM de cada modulo.
- **Entrada/comando:** `tests.test_clientes` y `tests.test_sucursales`:
  creacion, listado, consulta, datos invalidos, 404 y RUT duplicado.
- **Esperado:** Rutas y persistencia coherentes con el contrato.
- **Obtenido:** Sus 14 pruebas pasaron dentro de la suite completa.
- **Responsable/estado:** Gabriel; aprobado en la suite completa.

## Auditoria global

Se aplico Alembic desde una SQLite vacia y el seeder creo 2 clientes,
2 sucursales, 11 vehiculos y 2 reservas. OpenAPI expuso las 15 operaciones
de negocio; 16 solicitudes HTTP de los cuatro modulos respondieron segun lo
esperado. Tras detener e iniciar Uvicorn con la misma base y sin repetir el
seeder, `GET /vehiculos/{id}` devolvio el precio actualizado en el primer
proceso. La suite completa aprobo 53 pruebas, incluido el rollback conjunto
del vencimiento y una actualizacion fallida de vehiculo.
