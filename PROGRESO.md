# Progreso del equipo

## Piero Soto: base compartida y vehiculos

- Etapas 1 a 5 completadas: base, modelo, datos de demostracion, CRUD,
  consultas, pruebas, documentacion y PR de su modulo.
- Rama `feat/vehiculos`; PR #1 abierto hacia `main`:
  https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/1
  La fusion necesita revision y autorizacion.
- Cinco commits de desarrollo verificados: `579303e` (modelo y DTO),
  `2ca4a92` (datos demo), `0d8fa40` (CRUD), `26815be` (consultas) y
  `6ba2ea0` (pruebas manuales y documentacion).
- Decisiones: filtrar, ordenar y paginar en ese orden; calcular el total antes
  de paginar; resolver empates por ID ascendente; comprobar estados e historial
  antes de guardar cambios.
- Pruebas propias: 15 casos automatizados y 33 solicitudes de
  `tests_manual/vehiculos.http` aprobados. Dependencias instaladas y API
  ejecutada desde el entorno virtual nuevo.
- `main` ya incluye el PR #2 de Roberto. El merge `ec0d0a0` incorpora
  reservas a `feat/vehiculos` y resuelve los conflictos con el PR #1.
- Siguiente paso: conectar los vencimientos de reservas con las operaciones
  de vehiculos, revisar el PR #1 y fusionarlo con autorizacion.

## Gabriel Rivas: clientes y sucursales

- Responsable de las entidades, DTO, repositorios, servicios, rutas, pruebas y
  documentacion de clientes y sucursales.
- Todavia no se observa un PR de estos modulos en el repositorio compartido.
  Su codigo y pruebas no se han revisado ni integrado aqui.

## Roberto Gonzalez: reservas

- PR #2 fusionado en `main`:
  https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/2
  Incluye entidad, DTO, repositorio, servicio, cuatro rutas, pruebas y
  documentacion del modulo de reservas.
- Despues del merge local, las 30 pruebas automatizadas de vehiculos y
  reservas pasaron juntas. Tambien se comprobo por HTTP reservar, cancelar y
  recuperar la disponibilidad de un vehiculo; el esquema Swagger muestra
  ambos modulos.
- Evidencia Git por aclarar: los seis commits del PR #2 muestran como autor
  `Dev Reservas <dev.reservas@example.invalid>`, aunque Roberto abrio el PR y
  aparece como committer. Revisar con el la atribucion de sus commits sin
  modificar su historial por cuenta ajena.

## Integracion y pendientes del grupo

- Conectar `procesar_vencimientos()` antes de consultas y operaciones de
  vehiculos que dependan de la disponibilidad. Las pruebas completas entre
  modulos siguen pendientes.
- Integrar clientes y sucursales cuando Gabriel entregue su PR; verificar
  referencias, RUT unico y funcionamiento conjunto de los 15 endpoints.
- Repositorio anterior privado; nuevo repositorio publico
  `PieroSotoUCT/backend-2026-concesionaria-api`. Los ocho commits previos se
  reprodujeron sin prompt ni rubrica, conservando mensajes, autores y fechas;
  los hashes cambiaron al excluir esos archivos del historial.
- Confirmar con el docente el numero de grupo, la autorizacion de un equipo de
  tres, el nombre del repositorio, las fechas y la formula de nota de la guia.
