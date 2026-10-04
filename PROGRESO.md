# Progreso

## Mi parte: base y vehiculos

- Etapa 1: base local terminada; creacion y publicacion del remoto pendientes.
- Rama: `main` local. El commit de base se consulta con `git log -1`.
- Decisiones: cuatro colecciones compartidas por ID, contadores sin reutilizacion,
  errores uniformes y fecha local del servidor. Ver `CONTRATO.md`.
- Pruebas: instalacion en entorno virtual; inicio de Uvicorn; `/health` 200;
  OpenAPI con solo `/health`; ruta inexistente 404 y metodo incorrecto 405,
  ambos con formato uniforme. La validacion 422 espera rutas con DTO.
- Siguiente paso: revisar el commit inicial y, con autorizacion, crear el
  repositorio publico y publicar `main`. Luego comenzar la Etapa 2.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Nombres reales, numero de grupo y autorizacion docente para tres integrantes:
  pendientes. Repositorio publico solicitado; falta crear o conectar remoto.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
