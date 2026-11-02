# Guion breve para la defensa

La guía indica 10 minutos de exposición, 5 de preguntas y un máximo de
15 diapositivas. Como se sortea quién expone, los tres integrantes deben
ensayar el guion completo. Propuesta: 9 diapositivas, una por bloque.

| Tiempo | Tema | Qué mostrar y explicar |
| --- | --- | --- |
| 0:00–0:45 | Problema y alcance | La API administra sucursales, clientes, vehículos y reservas; tiene 15 operaciones de negocio. |
| 0:45–1:45 | Arquitectura | Una petición pasa por router, esquema Pydantic, servicio, repositorio ORM y SQLite. El servicio aplica reglas; el repositorio consulta datos. |
| 1:45–2:45 | Modelo de datos | Mostrar `docs/diagramas.md`: sucursal 1:N vehículos, cliente 1:N reservas y vehículo 1:N reservas históricas. Explicar claves foráneas y RUT único. |
| 2:45–3:45 | Persistencia | Alembic crea y actualiza tablas; el seeder opcional carga 2 clientes, 2 sucursales, 11 vehículos y 2 reservas en una base vacía. |
| 3:45–5:15 | API | En Swagger, mostrar los cuatro grupos de rutas, un ejemplo de POST y GET, y el error común `{error:{code,message,details:[]}}`. |
| 5:15–6:45 | Reglas de negocio | Demostrar que no se vende un vehículo reservado, que no se duplica una reserva activa y que un vencimiento libera disponibilidad. Explicar 409 frente a 422. |
| 6:45–8:15 | Consulta de vehículos | Aplicar filtro, orden y paginación; `total` se calcula antes de paginar. Mostrar un PATCH parcial y un DELETE 204 sin cuerpo. |
| 8:15–9:15 | Pruebas y reinicio | Citar las 53 pruebas aisladas y las evidencias. Detener e iniciar Uvicorn con la misma SQLite sin repetir el seeder; consultar el dato conservado. |
| 9:15–10:00 | Cierre | Resumir qué aporta cada módulo y señalar dónde están contrato, diagramas y evidencias en el repositorio. |

## Preguntas que todos deben poder responder

- **¿Por qué persisten los datos al reiniciar?** Las operaciones confirman transacciones en un archivo SQLite; Uvicorn puede reiniciarse sin reconstruirlo. Alembic prepara el esquema y el seeder solo agrega ejemplos a una base vacía.
- **¿Dónde se valida una entrada?** Pydantic comprueba tipos, rangos y campos; los servicios verifican reglas que requieren consultar la base.
- **¿Qué pasa si falla una operación tras procesar vencimientos?** Vehículos y reservas procesan vencimientos en la misma sesión de su operación. La transacción se revierte si aparece un error; hay una prueba específica de ese rollback.
- **¿Qué significan 404, 409 y 422?** Recurso ausente, conflicto con el estado o una regla, y entrada inválida, respectivamente. Un DELETE exitoso responde 204 sin cuerpo.
- **¿Cómo se comprueba filtro y paginación?** El repositorio filtra, ordena y luego pagina; devuelve el total anterior a la paginación. Las pruebas verifican IDs, totales y desempate.

Para la demostración usen una SQLite temporal nueva. Los comandos de
instalación, migración, carga y arranque están en `README.md`; los casos
reproducibles y resultados están en `docs/evidencias-pruebas.md`.
