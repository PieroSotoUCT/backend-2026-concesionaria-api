# Progreso del equipo

## Piero Soto: base compartida y vehiculos

- Etapas 1 a 5 completas. El PR #1 de vehiculos se fusiono en `main` mediante
  `69211fd`. Se conservan los commits de modelo `579303e`, datos demo
  `2ca4a92`, CRUD `0d8fa40`, consultas `26815be` y pruebas/documentacion
  `6ba2ea0` como evidencia individual.
- Pruebas propias realizadas: 15 casos automatizados y 33 solicitudes de
  `tests_manual/vehiculos.http` sobre datos de demostracion.
- Etapa 6 en curso: la rama local `fix/integracion-y-progreso` conecta la
  revision de vencimientos antes de consultas y operaciones de vehiculos.
  Las 32 pruebas automatizadas de vehiculos y reservas pasan juntas.
- Siguiente paso: incorporar esta correccion a `main` mediante un PR autorizado
  y revisar la integracion del PR #3 cuando Gabriel resuelva su conflicto.

## Gabriel Rivas: clientes y sucursales

- Responsable de entidades, DTO, repositorios, servicios, rutas, pruebas y
  documentacion de clientes y sucursales.
- El PR #3 esta abierto hacia `main` y presenta un conflicto en `app/main.py`:
  https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/3
  Debe actualizar su rama y conservar los routers de los cuatro modulos y
  la carga de datos demo al resolverlo.
- Su rama muestra cuatro commits de desarrollo; la rubrica pide al menos cinco
  propios y significativos. Los commits usan el autor `Nvyffrvn19` con un
  correo local del Mac; Gabriel debe comprobar su atribucion en GitHub.
- Sus seis endpoints y las pruebas del modulo aun no estan en `main`.

## Roberto Gonzalez: reservas

- El PR #2 esta fusionado en `main` mediante `203cd81`:
  https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/2
  Aporta entidad, DTO, repositorio, servicio, cuatro rutas, pruebas y
  documentacion de reservas.
- Evidencia Git por aclarar con Roberto: los seis commits del PR #2 muestran
  como autor `Dev Reservas <dev.reservas@example.invalid>`, aunque el PR y
  los committers pertenecen a su cuenta. No se ha modificado su historial.

## Integracion y pendientes del grupo

- `main` publica nueve endpoints de negocio: cinco de vehiculos y cuatro de
  reservas. Los seis de clientes y sucursales dependen del PR #3.
- Tras integrar a Gabriel, probar referencias, RUT unico, segunda reserva,
  cancelacion, vencimiento y los 15 endpoints del conjunto.
- Repositorio anterior privado; el nuevo repositorio publico excluye prompt y
  rubrica del historial. La migracion conservo mensajes, autores y fechas de
  los ocho commits previos; sus hashes cambiaron al excluir esos archivos.
- Confirmar con el docente el numero de grupo, la autorizacion de un equipo de
  tres, el nombre del repositorio, las fechas y la formula de nota de la guia.
