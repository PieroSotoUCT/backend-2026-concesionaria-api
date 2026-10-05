# Progreso

## Mi parte: base y vehiculos

- Etapas 1 a 5 terminadas: base, modelo, ejemplos, CRUD, consultas,
  documentacion y entrega de mi parte para revision.
- Rama: `feat/vehiculos`, publicada en el repositorio nuevo. PR #1 abierto
  hacia `main`: https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/1
  La fusion requiere revision y autorizacion.
- Migracion autorizada: repositorio anterior privado; nuevo repositorio
  publico `PieroSotoUCT/backend-2026-concesionaria-api`. Se reprodujeron los
  ocho commits previos sin archivos de referencia, conservando mensajes,
  autores y fechas. Los hashes cambiaron al excluir archivos del historial.
  Los patrones correspondientes estan excluidos por .gitignore.
- Cinco commits de desarrollo verificados: `579303e` (modelo y DTO),
  `2ca4a92` (ejemplos), `0d8fa40` (CRUD), `26815be` (consultas) y
  `6ba2ea0` (pruebas manuales y documentacion).
- Decisiones: filtrar, ordenar y paginar; total antes de paginar; empates
  por ID ascendente. Se conservan las reglas de disponibilidad e historial.
- Pruebas: 15 casos automatizados aprobados con
  `python -m unittest discover -s tests -v`, y 33 solicitudes del archivo
  `tests_manual/vehiculos.http` verificadas en orden con un servidor temporal.
  Instalacion de dependencias comprobada en el entorno virtual nuevo.
- Siguiente paso: revisar y fusionar el PR con autorizacion. Las etapas 6 a 8
  corresponden a integracion y cierre del equipo cuando lleguen sus modulos.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Equipo registrado: Piero Soto (base y vehiculos), Gabriel Rivas (clientes y
  sucursales) y Roberto Gonzalez (reservas). Numero de grupo y autorizacion
  docente para tres integrantes: pendientes. Repositorio nuevo conectado,
  `main` y `feat/vehiculos` publicados hasta los avances indicados arriba.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
