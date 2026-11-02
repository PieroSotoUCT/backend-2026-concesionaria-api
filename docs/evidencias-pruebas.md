# Evidencias de pruebas

## Entorno y comandos ejecutados

Las pruebas propias de reservas e integracion usan una SQLite en la carpeta
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
```

Resultados reales:

- Ambos modulos juntos: 20 pruebas, correcto.
- `test_reservas`: 17 pruebas, correcto.
- `test_orm_integracion`: 3 pruebas, correcto.
- `compileall` para `app` y `tests`, y `git diff --check`: correctos.

La suite completa no se ejecuto: las pruebas existentes de clientes y
sucursales aun preparan colecciones en memoria, y las de vehiculos dependen de
datos demo. No se comprobo que esas pruebas aislen la base antes de importar
la aplicacion. Sus resultados se dejan pendientes; no se ejecutaron contra la
base configurada por defecto.

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
  DELETE; el CRUD completo de vehiculos queda pendiente en VEH-CRUD-01.

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

## Casos pendientes de integracion

### VEH-CRUD-01 — CRUD completo de vehiculos

- **Requisito:** Crear, consultar, actualizar y eliminar segun las reglas del
  contrato.
- **Preparacion:** Pendiente de fixtures ORM y base temporal propios del
  modulo.
- **Entrada/comando:** Pendiente de validacion con el responsable del modulo.
- **Esperado:** Respuestas y estados coherentes con el contrato.
- **Obtenido:** No ejecutado; no se registra un resultado supuesto.
- **Responsable/estado:** Piero; pendiente.

### VEH-QUERY-01 — Filtros, orden y paginacion

- **Requisito:** Verificar filtros, orden, desempate por ID, limites y
  metadatos de paginacion.
- **Preparacion:** Pendiente de ejecutar pruebas ORM aisladas del modulo de
  vehiculos.
- **Entrada/comando:** Pendiente; no ejecutar el test actual del modulo hasta
  confirmar que no usa la base de desarrollo.
- **Esperado:** Resultados y totales conforme a `CONTRATO.md`.
- **Obtenido:** No ejecutado; no se registra un resultado supuesto.
- **Responsable/estado:** Piero; pendiente.

### INT-CLIENTES-SUCURSALES-01 — Persistencia y reglas de clientes y sucursales

- **Requisito:** Verificar altas, consultas, referencias y validaciones de los
  modulos integrados.
- **Preparacion:** Pendiente de reemplazar el sembrado en memoria por fixtures
  ORM temporales.
- **Entrada/comando:** Pendiente; las pruebas existentes aun acceden a
  colecciones en memoria.
- **Esperado:** Rutas y persistencia coherentes con el contrato.
- **Obtenido:** No ejecutado; no se registra un resultado supuesto.
- **Responsable/estado:** Gabriel; pendiente.

## Auditoria global pendiente

No se ejecutaron la suite completa, la migracion integral desde cero, el
seeder de todas las entidades ni la recuperacion de disponibilidad mediante
`GET /vehiculos`. Esas comprobaciones requieren completar el aislamiento y la
evidencia de los modulos de Piero y Gabriel. No se alteraron sus pruebas ni
sus implementaciones.
