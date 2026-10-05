# Progreso

## Mi parte: base y vehiculos

- Etapa 1: base terminada y publicada en `origin/main`.
- Etapa 2: modelo, DTO y datos de demostracion terminados en la rama local
  `feat/vehiculos`. La rama incluye las correcciones locales de nombres;
  no hay push ni PR de esta rama.
- Commits observados: `ac70f05` (entidad y DTO); los ejemplos se registran
  en el commit siguiente de esta rama. Consultar `git log --oneline`.
- Decisiones: cuatro colecciones compartidas, IDs sin reutilizacion, errores
  uniformes, Pydantic v2 y carga demo explicita solo con memoria vacia.
- Pruebas: DTO validos e invalidos; PATCH parcial, nulo y vacio; carga de
  2 sucursales, 12 vehiculos, 1 cliente y 2 reservas; referencias y estados;
  rechazo de segunda carga; manejador 422 directo; Uvicorn con ejemplos y
  `/health` 200. El 422 por HTTP espera los endpoints de la Etapa 3.
- Siguiente paso: Etapa 3, repositorio, servicio y cinco rutas de vehiculos.

## Integracion y pendientes del grupo

- Modulos de clientes, sucursales y reservas: a cargo de los companeros.
- Conexion del vencimiento de reservas con consultas de vehiculos: pendiente
  hasta recibir ese modulo.
- Equipo registrado: Piero Soto (base y vehiculos), Gabriel Rivas (clientes y
  sucursales) y Roberto Gonzalez (reservas). Numero de grupo y autorizacion
  docente para tres integrantes: pendientes. Repositorio publico conectado
  y `main` publicado.
- Fechas de entrega y formula de nota de la guia: confirmar con el docente.
