# Progreso del equipo

## Estado integrado en `main`

`origin/main` esta en `615cc3c`. Incorpora PR #1 (vehiculos), PR #2
(reservas), PR #3 (clientes y sucursales) y PR #4 (SQLAlchemy y Alembic).
Registra 15 endpoints de negocio y `GET /health`. Tener codigo integrado no
equivale aun a cumplir todos los requisitos de la guia.

## Piero Soto: base compartida y vehiculos

- El PR #1 se fusiono en `main` mediante `69211fd`. Los cinco commits de
  desarrollo de vehiculos siguen en el historial: `579303e`, `2ca4a92`,
  `0d8fa40`, `26815be` y `6ba2ea0`.
- Rama actual `fix/base-vehiculos-integracion`: commits `b3f70f4` (base,
  migracion reproducible y pruebas temporales) y `363aada` (repositorio ORM
  de vehiculos y vencimientos) subidos a `origin`.
- Etapa 3 guardada en `4b4a078`: migracion nueva para IDs,
  `tests/test_vehiculos.py` con fixtures ORM y ejemplos `.http` corregidos.
  Resultado: 18 pruebas propias aprobadas y 33 solicitudes manuales con
  codigos esperados sobre SQLite temporal. Detalle en
  [docs/avance-piero.md](docs/avance-piero.md).
- Etapa 4 documenta el estado real en README y contrato y registra pendientes
  de los otros modulos sin modificar sus archivos. La integracion completa
  depende de las correcciones y entregables de sus responsables.

## Gabriel Rivas: clientes y sucursales

- El PR #3 se fusiono mediante `3284e81`. Hay seis rutas registradas y
  servicios que persisten con ORM.
- `app/services/clientes.py` y `app/services/sucursales.py` aun hacen
  consultas SQLAlchemy directamente. Sus repositorios conservan codigo
  antiguo sobre colecciones inexistentes. Gabriel debe mover el acceso ORM
  a esos repositorios sin cambiar el contrato HTTP.
- En SQLite temporal migrada, `tests.test_clientes` y
  `tests.test_sucursales` fallan: intentan acceder a `datos.vehiculos` y sus
  servidores de prueba terminan antes de iniciar. Gabriel debe migrar sus
  fixtures y establecer la URL de prueba antes de importar `app.db`.
- `app/datos_demo.py` crea solo un cliente; la guia pide al menos dos por
  entidad. Faltan `docs/diagramas.md` y diagramas de clases y datos.

## Roberto Gonzalez: reservas y pruebas del conjunto

- El PR #2 se fusiono mediante `203cd81` y el PR #4 mediante `615cc3c`.
  Reservas usa ORM y tiene cuatro rutas.
- En SQLite temporal migrada, `tests.test_reservas` falla por referencias a
  `datos.vehiculos` y por el arranque del servidor. En
  `tests.test_orm_integracion`, uno de dos casos falla porque presupone
  `cliente_id=1` tras limpiar registros; los IDs ahora siguen creciendo.
  Roberto debe crear fixtures ORM propias con IDs capturados y aislar la base
  antes de importar `app.db`.
- Para integrar vencimientos en una sola transaccion con vehiculos, Roberto
  debe exponer una funcion que reciba la sesion ORM activa. Falta
  `docs/evidencias-pruebas.md` con seis casos reproducibles, incluido reinicio
  real del proceso.
- Los commits antiguos del PR #2 muestran el autor
  `Dev Reservas <dev.reservas@example.invalid>`; Roberto debe confirmar su
  atribucion. No se reescribio su historial.

## Entrega del grupo

- Confirmar con el docente el numero y nombre del grupo, la autorizacion
  para tres integrantes y la fecha exacta.
- Completar seeder, diagramas y evidencias; ejecutar la suite entera solo
  despues de asegurar bases temporales para todos los procesos de prueba.
- Desde una copia limpia, migrar, cargar ejemplos, verificar OpenAPI y los
  15 endpoints; demostrar persistencia tras reiniciar sin recargar el seeder.
