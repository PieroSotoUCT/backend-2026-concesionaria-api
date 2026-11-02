# Avance de Gabriel — Parte 2

## Responsabilidades

Implementación de los módulos de clientes y sucursales, carga de datos ficticios, documentación y pruebas asociadas.

## Estado general

- [x] Entidad, esquemas, repositorio, servicio y rutas de clientes.
- [x] Entidad, esquemas, repositorio, servicio y rutas de sucursales.
- [x] Validaciones y manejo de errores según el contrato.
- [x] Documentación OpenAPI de los endpoints.
- [x] Carga explícita de datos ficticios mediante ORM.
- [x] Documentación de los módulos.
- [x] Diagramas de clases y relaciones.
- [x] Archivo de pruebas HTTP manuales.
- [x] Pruebas unitarias de clientes y sucursales.
- [x] Revisión de calidad del código con Ruff.
- [x] Verificación de diferencias con Git.
- [ ] Revisión final de los documentos y del estado de Git.
- [ ] Commit final de estos cambios.

## Clientes

Se implementaron los siguientes endpoints:

- `POST /clientes`: registra un cliente.
- `GET /clientes`: lista los clientes.
- `GET /clientes/{id}`: obtiene un cliente por su ID.

Las rutas incluyen documentación OpenAPI con resúmenes, descripciones y respuestas esperadas. El ID debe ser positivo y lo asigna el servidor al crear el cliente.

## Sucursales

Se implementaron los siguientes endpoints:

- `POST /sucursales`: registra una sucursal.
- `GET /sucursales`: lista las sucursales.
- `GET /sucursales/{id}`: obtiene una sucursal por su ID.

Las rutas incluyen documentación OpenAPI con resúmenes, descripciones y respuestas esperadas. El ID debe ser positivo y lo asigna el servidor al crear la sucursal.

## Datos de demostración

Se actualizó `app/datos_demo.py` para cargar datos ficticios mediante ORM. La ejecución es explícita desde la raíz del proyecto:

```bash
python -m app.datos_demo
```

El seeder incorpora datos relacionados de sucursales, clientes, vehículos y reservas. También verifica que las tablas estén vacías antes de insertar los registros, evitando duplicar datos existentes.

## Documentación

Se incorporaron documentos para describir el avance, los módulos implementados y sus diagramas:

- `docs/avance-gabriel.md`
- `docs/clientes-sucursales.md`
- `docs/diagramas.md`

## Pruebas

Se implementaron pruebas unitarias para los módulos de clientes y sucursales.

**Resultado:** 12 pruebas aprobadas mediante:

```bash
python -m unittest tests.test_clientes tests.test_sucursales -v
```

También se realizaron pruebas HTTP manuales utilizando REST Client, verificando:

- Listado de clientes y sucursales.
- Creación de clientes y sucursales.
- Consulta por ID.
- Respuesta 404 para recursos inexistentes.
- Respuesta 409 para RUT duplicado.

El archivo de solicitudes manuales se encuentra en `tests_manual/clientes_sucursales.http`.

## Calidad del código

Se ejecutaron las siguientes verificaciones:

- Ruff: `All checks passed!` en los archivos del módulo.
- Pruebas unitarias: 12 de 12 aprobadas.
- `git diff --check`: sin observaciones.

## Estado de entrega

Los módulos de clientes y sucursales están implementados y sus pruebas unitarias y manuales han sido verificadas. Queda pendiente la revisión final de los documentos y la preparación del commit correspondiente.