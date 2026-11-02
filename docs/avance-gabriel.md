# Avance de Gabriel — Parte 2

## Responsabilidades

Implementación de los módulos de clientes y sucursales, carga de datos ficticios mediante ORM, documentación y pruebas asociadas.

Este documento registra el avance individual de Gabriel. La integración general del proyecto corresponde al equipo.

## Estado general

- [x] Implementación de entidades, DTO, repositorios, servicios y rutas de clientes.
- [x] Implementación de entidades, DTO, repositorios, servicios y rutas de sucursales.
- [x] Implementación de las seis rutas HTTP asignadas.
- [x] Normalización del RUT y detección de duplicados.
- [x] Validación de formato de correo electrónico mediante `EmailStr`.
- [x] Rechazo de campos compuestos únicamente por espacios.
- [x] Manejo verificado de errores de integridad y rollback.
- [x] Unificación definitiva de los DTO de clientes.
- [x] Verificación de las respuestas HTTP documentadas en OpenAPI.
- [x] Seeder ORM con al menos dos registros por entidad.
- [x] Seeder con suficientes vehículos para demostrar paginación.
- [x] Prueba de relaciones ORM del seeder.
- [x] Prueba de rechazo de segunda ejecución del seeder.
- [ ] Verificación del seeder después de aplicar migraciones Alembic.
- [x] Archivo de pruebas HTTP manuales implementado y ampliado.
- [x] Pruebas automatizadas de clientes y sucursales.
- [x] Ampliación de pruebas para cubrir validaciones y conflictos de integridad.
- [ ] Prueba de persistencia después de reiniciar un proceso.
- [x] Documentos de módulos y diagramas actualizados.
- [x] Revisión de documentación y diagramas.
- [x] Verificación de Ruff en los archivos de responsabilidad individual.
- [x] Revisión de Git, commits y publicación de la rama.
- [ ] Verificación final de todos los criterios de entrega individual.

## Clientes

Endpoints implementados:

- `POST /clientes` — HTTP 201.
- `GET /clientes` — HTTP 200.
- `GET /clientes/{id}` — HTTP 200.

El servidor asigna automáticamente el ID.

Se utiliza SQLAlchemy ORM para registrar y consultar clientes.

El esquema `ClienteCrear` utiliza Pydantic para validar los datos de entrada.

Las validaciones incluyen:

- RUT de entre 3 y 20 caracteres.
- Nombre de entre 2 y 100 caracteres.
- Correo electrónico válido mediante `EmailStr`.
- Teléfono de entre 1 y 30 caracteres.
- Dirección de entre 1 y 200 caracteres.
- Rechazo de campos adicionales.
- Eliminación de espacios exteriores mediante `str_strip_whitespace=True`.

### Normalización y duplicidad del RUT

El RUT se normaliza mediante:

1. Eliminación de puntos.
2. Eliminación de espacios.
3. Conversión de letras a mayúsculas.

Se implementó una consulta previa para detectar RUT duplicados y una restricción UNIQUE en la base de datos.

Cuando se produce un conflicto de unicidad, el servicio devuelve:

- HTTP 409.
- Código `DUPLICATE_RESOURCE`.

También se implementó `_es_rut_duplicado()` para distinguir específicamente los conflictos de RUT de otros errores de integridad.

### Manejo transaccional

Se verificó que una violación real de unicidad produce un rollback completo.

La prueba comprobó que no quedaran inserciones parciales después del conflicto.

Se incorporaron pruebas automatizadas para verificar tanto la detección del error como su respuesta controlada.

## Sucursales

Endpoints implementados:

- `POST /sucursales` — HTTP 201.
- `GET /sucursales` — HTTP 200.
- `GET /sucursales/{id}` — HTTP 200.

El servidor asigna automáticamente el ID.

Se utiliza SQLAlchemy ORM para registrar, listar y consultar sucursales.

Las validaciones del DTO incluyen:

- Nombre de entre 2 y 100 caracteres.
- Dirección de entre 1 y 200 caracteres.
- Ciudad de entre 2 y 100 caracteres.
- Teléfono de entre 1 y 30 caracteres.
- Horario de atención de entre 1 y 120 caracteres.
- Rechazo de campos adicionales.
- Eliminación de espacios exteriores.
- Rechazo de valores compuestos únicamente por espacios.

Se realizaron comprobaciones de validación para los campos de sucursal y se incorporaron pruebas automatizadas para el módulo.

## Datos de demostración

Archivo: `app/datos_demo.py`

Comando de ejecución:

```bash
python -m app.datos_demo
```

El seeder carga datos ficticios mediante SQLAlchemy ORM y establece las relaciones entre las cuatro entidades.

### Registros comprobados

| Entidad | Cantidad |
|---|---:|
| Clientes | 2 |
| Sucursales | 2 |
| Vehículos | 11 |
| Reservas | 2 |
| **Total** | **17** |

### Prueba aislada del seeder

Se realizó una prueba utilizando SQLite en memoria mediante la variable de entorno:

`CONCESIONARIA_DATABASE_URL=sqlite://`

Resultados:

1. Inicialización de tablas ORM: correcta.
2. Primera ejecución del seeder: correcta.
3. Clientes registrados: 2.
4. Sucursales registradas: 2.
5. Vehículos registrados: 11.
6. Reservas registradas: 2.
7. Vehículos con sucursal válida: 11 de 11.
8. Reservas con cliente y vehículo válidos: 2 de 2.

Resultado:

```text
Clientes, sucursales, vehiculos, reservas: [2, 2, 11, 2]
Vehiculos con sucursal valida: 11 / 11
Reservas con relaciones validas: 2 / 2
RESULTADO: CORRECTO
```

### Paginación de vehículos

Se verificó el funcionamiento del servicio de paginación:

| Consulta | Resultado |
|---|---:|
| Primera página | 10 vehículos |
| Segunda página | 1 vehículo |
| Total | 11 vehículos |
| Total de páginas | 2 |

### Protección contra duplicaciones

El seeder verifica que las cuatro tablas estén vacías antes de insertar los datos.

Si encuentra registros existentes, rechaza la operación mediante:

`RuntimeError: Los datos demo requieren una base de datos completamente vacía.`

También se verificó que una segunda ejecución no modificara los registros existentes.

En una comprobación sobre la base SQLite temporal se conservaron los siguientes conteos:

```text
Clientes, sucursales, vehiculos, reservas: [3, 3, 11, 2]
CORRECTO: registros conservados
```

### Pendientes del seeder

- Verificar su ejecución después de aplicar migraciones Alembic en una base temporal.
- Coordinar con Piero cualquier integración opcional de la carga de datos desde `app/main.py`.

## Pruebas de clientes y sucursales

Se implementaron pruebas aisladas utilizando:

- `unittest`.
- `FastAPI TestClient`.
- SQLAlchemy.
- SQLite en memoria.
- `unittest.mock.patch` para aislar las sesiones de prueba.

Comando ejecutado:

```bash
python -m unittest tests.test_clientes tests.test_sucursales -v
```

### Resultado final

**14 pruebas automatizadas aprobadas.**

| Módulo | Pruebas aprobadas |
|---|---:|
| Clientes | 9 |
| Sucursales | 5 |
| **Total** | **14** |

### Casos comprobados de clientes

- Creación de clientes.
- Normalización del RUT.
- Listado de clientes.
- Consulta de clientes existentes.
- Respuesta 404 para clientes inexistentes.
- Respuesta 409 para RUT duplicados.
- Validación de correo electrónico.
- Respuesta 422 para datos faltantes.
- Distinción entre errores de unicidad y otros errores de integridad.
- Conflicto real de unicidad y rollback.

### Casos comprobados de sucursales

- Creación y asignación automática de ID.
- Validación de datos incorrectos.
- Listado de sucursales.
- Consulta de sucursales existentes.
- Respuesta 404 para sucursales inexistentes.

### Comprobaciones adicionales

Se realizaron comprobaciones directas con Pydantic para verificar el rechazo de campos compuestos únicamente por espacios, tanto en clientes como en sucursales.

También se comprobó el rechazo de correos inválidos y campos adicionales.

### Pruebas HTTP manuales

Archivo:

`tests_manual/clientes_sucursales.http`

Se preparó y amplió el archivo de solicitudes para REST Client de Visual Studio Code.

Incluye operaciones de creación, listado y consulta, además de solicitudes para comprobar errores de validación, recursos inexistentes y RUT duplicados.

Las solicitudes adicionales preparadas no se consideran automáticamente pruebas manuales ejecutadas.

### Pendiente de pruebas

- Comprobar persistencia después de reiniciar un proceso de aplicación.
- Completar el registro de ejecución individual de todas las solicitudes HTTP manuales.

## Documentación

Se actualizaron los siguientes archivos:

- `docs/clientes-sucursales.md`: descripción de los módulos, endpoints, validaciones y errores.
- `docs/diagramas.md`: diagramas de clases y datos, atributos, claves y relaciones.
- `docs/avance-gabriel.md`: registro actualizado del trabajo individual y sus evidencias.

Se revisaron las relaciones entre clientes, sucursales, vehículos y reservas, además de las claves primarias, foráneas y la restricción UNIQUE del RUT.

## Calidad del código

Se ejecutó Ruff sobre los archivos correspondientes a clientes, sucursales, seeder y pruebas.

Resultado:

```text
All checks passed!
```

También se ejecutó Ruff sobre el proyecto completo.

En esa revisión se encontraron nueve observaciones en archivos compartidos y módulos de vehículos y reservas. Estas observaciones no corresponden a los archivos de mi responsabilidad que fueron verificados individualmente.

Se ejecutó:

```bash
git diff --check
```

Resultado: sin observaciones.

## Calidad y Git

Rama de trabajo:

`feat/parte-2-clientes-sucursales`

Se registraron ocho commits en el historial de trabajo de la rama.

### Commit final

`28598f6`

Mensaje:

`feat(clientes-sucursales): completar validaciones, seeder y documentación`

El commit incluye:

- Validaciones adicionales.
- Manejo de conflictos de integridad.
- Ampliación del seeder.
- Actualización de esquemas.
- Ampliación de pruebas.
- Documentación y diagramas.

Se publicó correctamente la rama en GitHub.

### Pull Request

Pull Request: [#5 — backend-2026-concesionaria-api](https://github.com/PieroSotoUCT/backend-2026-concesionaria-api/pull/5)

Rama de origen:

`feat/parte-2-clientes-sucursales`

Rama de destino:

`main`

El commit `28598f6` aparece en el Pull Request.

Estado: abierto, pendiente de revisión e integración por parte del equipo.

## Estado de entrega

La implementación individual de los módulos de clientes y sucursales se encuentra completada y publicada para revisión.

Se verificaron las operaciones HTTP asignadas, las validaciones, la normalización del RUT, la restricción de unicidad, el manejo transaccional y las relaciones ORM.

Se obtuvieron 14 pruebas automatizadas aprobadas y Ruff pasó correctamente en los archivos correspondientes a mi responsabilidad.

El seeder fue probado en SQLite en memoria, generando 17 registros relacionados y permitiendo demostrar la paginación de vehículos.

La documentación de módulos y diagramas fue actualizada y el trabajo se publicó mediante el Pull Request #5.

### Verificaciones que permanecen pendientes

- Ejecución del seeder después de aplicar migraciones Alembic en una base temporal.
- Prueba de persistencia después de reiniciar un proceso.
- Revisión e integración del Pull Request por parte del equipo.

La responsabilidad individual de implementación de Gabriel está completada. Las verificaciones pendientes y la integración general deben distinguirse de las actividades de desarrollo ya finalizadas.

La implementación de vehículos, reservas y componentes compartidos corresponde a sus respectivos responsables.