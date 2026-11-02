# Progreso del equipo

## Estado de la integración

Las cuatro entidades (sucursales, clientes, vehículos y reservas) persisten
mediante SQLAlchemy en SQLite. Alembic crea el esquema y conserva las
relaciones. La API publica 15 operaciones de negocio y `GET /health`.

La suite conjunta ejecuta 53 pruebas en bases temporales y pasó sin fallos.
En una base nueva, Alembic y el seeder generaron 2 clientes, 2 sucursales,
11 vehículos y 2 reservas. Se verificaron OpenAPI, 16 solicitudes HTTP de
los cuatro módulos y un reinicio real de Uvicorn sin recargar el seeder;
el dato actualizado siguió disponible. Los casos reproducibles están en
[docs/evidencias-pruebas.md](docs/evidencias-pruebas.md).

## Aportes por integrante

- **Piero Soto:** conexión y migraciones, contrato y errores compartidos,
  repositorio y cinco rutas de vehículos, pruebas aisladas e integración
  final. Vehículos procesa vencimientos en la misma sesión y transacción.
  Los detalles de cada etapa están en [docs/avance-piero.md](docs/avance-piero.md).
- **Gabriel Rivas:** clientes, sucursales, seeder de cuatro entidades,
  diagramas y pruebas ORM de sus módulos. Su avance está en
  [docs/avance-gabriel.md](docs/avance-gabriel.md) y los diagramas en
  [docs/diagramas.md](docs/diagramas.md).
- **Roberto González:** reservas, vencimientos, pruebas de integración ORM
  y evidencia. Su avance está en [docs/avance-roberto.md](docs/avance-roberto.md).
  Sus commits antiguos con autor `Dev Reservas` están atribuidos en ese archivo.

El historial Git conserva al menos cinco commits significativos por
integrante, ramas individuales y los PR de trabajo. No se alteraron autores,
fechas ni commits anteriores.
