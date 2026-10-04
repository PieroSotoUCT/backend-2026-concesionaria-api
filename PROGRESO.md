# Progreso

## Mi parte: base y vehiculos

- Etapa 1: base terminada y publicada en `origin/main`.
- Rama: `main`. Commits propios observados: `955e10c` (base) y `a0bc267`
  (instrucciones de colaboracion). No hay PR todavia.
- Decisiones: cuatro colecciones compartidas por ID, contadores sin reutilizacion,
  errores uniformes y fecha local del servidor. Ver `CONTRATO.md`.
- Pruebas: instalacion en entorno virtual; inicio de Uvicorn; `/health` 200;
  OpenAPI con solo `/health`; ruta inexistente 404 y metodo incorrecto 405,
  ambos con formato uniforme. La validacion 422 espera rutas con DTO.
- Siguiente paso: al aprobar la Etapa 2, crear `feat/vehiculos` desde `main`
  y preparar modelo, DTO y datos de demostracion.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Nombres reales, numero de grupo y autorizacion docente para tres integrantes:
  pendientes. Repositorio publico conectado y `main` publicado.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
