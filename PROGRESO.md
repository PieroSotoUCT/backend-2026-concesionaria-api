# Progreso

## Mi parte: base y vehiculos

- Etapa 1: base terminada y publicada en `origin/main`.
- Etapas 2 y 3 terminadas: modelo, DTO, ejemplos y cinco endpoints CRUD.
- Rama local: `feat/vehiculos`, incluye las correcciones de nombres. Sin
  push ni PR. Commits previos verificados: `ac70f05` (modelo) y `5835a14`
  (ejemplos). El commit del CRUD se consulta con `git log -1 --oneline`.
- Decisiones: repositorio consulta colecciones comunes; servicio valida antes
  de guardar. Estados manuales prohibidos: 400; conflictos de estado o
  historial: 409. Listado completo provisional hasta la Etapa 4.
- Pruebas: 12 casos automatizados aprobados con
  `python -m unittest discover -s tests -v`: CRUD HTTP, errores uniformes,
  IDs no reutilizados, referencias, PATCH parcial/nulo, rechazo sin cambios
  parciales, estados incompatibles, historial activo/cancelado/vencido y OpenAPI.
- Siguiente paso: Etapa 4, filtros, orden, paginacion y coleccion vehiculos.http.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Equipo registrado: Piero Soto (base y vehiculos), Gabriel Rivas (clientes y
  sucursales) y Roberto Gonzalez (reservas). Numero de grupo y autorizacion
  docente para tres integrantes: pendientes. Repositorio publico conectado
  y `main` publicado.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
