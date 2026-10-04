# Progreso

## Mi parte: base y vehiculos

- Etapa 1: base local terminada y remoto publico creado; push pendiente.
- Rama: `main` local. Hay commits propios de base; consultar `git log`.
- Decisiones: cuatro colecciones compartidas por ID, contadores sin reutilizacion,
  errores uniformes y fecha local del servidor. Ver `CONTRATO.md`.
- Pruebas: instalacion en entorno virtual; inicio de Uvicorn; `/health` 200;
  OpenAPI con solo `/health`; ruta inexistente 404 y metodo incorrecto 405,
  ambos con formato uniforme. La validacion 422 espera rutas con DTO.
- Siguiente paso: con autorizacion, publicar `main` en `origin`. Luego
  comenzar la Etapa 2 en `feat/vehiculos`.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Nombres reales, numero de grupo y autorizacion docente para tres integrantes:
  pendientes. Repositorio publico conectado como `origin`, aun sin codigo.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
