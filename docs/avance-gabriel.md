# Avance de Gabriel — Parte 2

## 1. Responsabilidades

Implementación de los módulos de clientes y sucursales, carga de datos ficticios mediante ORM, documentación y pruebas asociadas.

Este documento registra el avance individual de Gabriel. La integración general del proyecto corresponde al equipo.

## 2. Estado general

- [x] Implementación de entidades, modelos ORM, DTO, repositorios, servicios y rutas de clientes.
- [x] Implementación de entidades, modelos ORM, DTO, repositorios, servicios y rutas de sucursales.
- [x] Implementación de las seis rutas HTTP asignadas.
- [x] Normalización del RUT.
- [x] Detección de RUT duplicados mediante consulta y restricción UNIQUE.
- [x] Validación del formato del correo electrónico mediante `EmailStr`.
- [x] Rechazo de campos compuestos únicamente por espacios.
- [x] Normalización de espacios exteriores mediante `str_strip_whitespace=True`.
- [x] Manejo específico de errores de integridad asociados al RUT duplicado.
- [x] Verificación de rollback ante conflictos de unicidad.
- [x] Eliminación del DTO duplicado de clientes.
- [x] Revisión de ejemplos y respuestas OpenAPI de los seis endpoints.
- [x] Seeder ORM con datos ficticios de las cuatro entidades.
- [x] Seeder con suficientes vehículos para demostrar paginación.
- [x] Verificación de relaciones ORM del seeder.
- [x] Verificación del rechazo de una segunda ejecución del seeder.
- [x] Prueba aislada del seeder en SQLite en memoria.
- [x] Archivo de pruebas HTTP manuales ampliado.
- [x] Pruebas automatizadas de clientes y sucursales.
- [x] Revisión de calidad del código con Ruff en los módulos correspondientes.
- [x] Documentación de módulos y diagramas actualizada.
- [ ] Verificación del seeder después de aplicar migraciones Alembic en una base temporal.
- [ ] Verificación de persistencia después de reiniciar un proceso.
- [ ] Ejecución y registro de todas las pruebas HTTP manuales.
- [ ] Revisión final de documentación y diagramas.
- [ ] Revisión final de Git y preparación del commit final.
- [ ] Verificación final de los criterios de entrega individual.
- [ ] Preparación del Pull Request hacia `main`.

## 3. Clientes

Se implementaron los siguientes endpoints:

| Método | Endpoint | Respuesta exitosa |
|---|---|---|
| POST | `/clientes` | 201 Created |
| GET | `/clientes` | 200 OK |
| GET | `/clientes/{id}` | 200 OK |

### Implementación

El módulo utiliza SQLAlchemy ORM para registrar, listar y consultar clientes.

El servidor asigna automáticamente el identificador al crear un cliente.

El esquema `ClienteCrear` establece las siguientes validaciones:

| Campo | Restricciones |
|---|---|
| `rut` | Texto de 3 a 20 caracteres |
| `nombre` | Texto de 2 a 100 caracteres |
| `correo` | Dirección de correo válida |
| `telefono` | Texto de 1 a 30 caracteres |
| `direccion` | Texto de 1 a 200 caracteres |

Se utiliza `ConfigDict` con las siguientes opciones:

- `extra="forbid"`: rechaza campos adicionales.
- `str_strip_whitespace=True`: elimina espacios al inicio y al final de los textos.

El correo electrónico se valida mediante `EmailStr`.

### Normalización del RUT

El servicio normaliza el RUT mediante:

1. Eliminación de puntos.
2. Eliminación de espacios.
3. Conversión de letras a mayúsculas.

Se evita registrar clientes con el mismo RUT normalizado.

La unicidad se respalda mediante una restricción UNIQUE en la base de datos.

### Manejo de duplicados

Se implementó la función `_es_rut_duplicado()` para identificar específicamente los errores de unicidad de la columna `clientes.rut`.

Cuando se detecta un conflicto, el servicio devuelve:

- HTTP: `409`.
- Código: `DUPLICATE_RESOURCE`.

Los errores de integridad que no corresponden a un RUT duplicado se vuelven a propagar, evitando convertirlos incorrectamente en conflictos de duplicidad.

También se comprobó que una transacción fallida realiza rollback y no conserva inserciones parciales.

## 4. Sucursales

Se implementaron los siguientes endpoints:

| Método | Endpoint | Respuesta exitosa |
|---|---|---|
| POST | `/sucursales` | 201 Created |
| GET | `/sucursales` | 200 OK |
| GET | `/sucursales/{id}` | 200 OK |

### Implementación

El módulo utiliza SQLAlchemy ORM para registrar, listar y consultar sucursales.

El servidor asigna automáticamente el identificador.

El esquema `SucursalCrear` establece las siguientes restricciones:

| Campo | Restricciones |
|---|---|
| `nombre` | Texto de 2 a 100 caracteres |
| `direccion` | Texto de 1 a 200 caracteres |
| `ciudad` | Texto de 2 a 100 caracteres |
| `telefono` | Texto de 1 a 30 caracteres |
| `horario_atencion` | Texto de 1 a 120 caracteres |

Se utiliza:

- `extra="forbid"` para rechazar campos adicionales.
- `str_strip_whitespace=True` para normalizar espacios exteriores.

Los valores que quedan vacíos después de la normalización son rechazados por las restricciones de longitud.

## 5. Documentación OpenAPI

Se verificó el esquema OpenAPI generado por FastAPI para los seis endpoints.

Resultados obtenidos:

| Endpoint | Respuestas declaradas |
|---|---|
| `GET /clientes` | 200 |
| `POST /clientes` | 201, 409, 422 |
| `GET /clientes/{id}` | 200, 404, 422 |
| `GET /sucursales` | 200 |
| `POST /sucursales` | 201, 422 |
| `GET /sucursales/{id}` | 200, 404, 422 |

La comprobación se realizó mediante:

```bash
python -c "from app.main import app; esquema = app.openapi(); [print(ruta, metodo.upper(), operacion.get('responses', {}).keys()) for ruta, metodos in esquema['paths'].items() if ruta.startswith(('/clientes', '/sucursales')) for metodo, operacion in metodos.items()]"
```

Los seis endpoints aparecen correctamente registrados en OpenAPI.

## 6. Datos de demostración

Archivo: `app/datos_demo.py`

Comando de ejecución:

```bash
python -m app.datos_demo
```

El seeder utiliza SQLAlchemy ORM para insertar datos ficticios relacionados de clientes, sucursales, vehículos y reservas.

### Registros de demostración

La carga verificada en una base SQLite aislada contempla:

| Entidad | Cantidad |
|---|---:|
| Clientes | 2 |
| Sucursales | 2 |
| Vehículos | 11 |
| Reservas | 2 |
| **Total** | **17** |

Los vehículos incorporan distintas marcas, modelos, años, precios, kilometrajes, transmisiones y condiciones.

### Verificación aislada

La prueba se ejecutó utilizando SQLite en memoria mediante:

`CONCESIONARIA_DATABASE_URL=sqlite://`

Se inicializaron las tablas ORM y posteriormente se ejecutó el seeder.

Resultados:

1. Inicialización de tablas ORM: correcta.
2. Primera ejecución del seeder: correcta.
3. Clientes registrados: 2.
4. Sucursales registradas: 2.
5. Vehículos registrados: 11.
6. Reservas registradas: 2.
7. Vehículos con sucursal válida: 11 de 11.
8. Reservas con cliente y vehículo válidos: 2 de 2.

Resultado final:

```text
Clientes, sucursales, vehiculos, reservas: [2, 2, 11, 2]
Vehiculos con sucursal valida: 11 / 11
Reservas con relaciones validas: 2 / 2
RESULTADO: CORRECTO
```

La prueba se realizó en una base en memoria, sin modificar la base de desarrollo `concesionaria.db`.

### Paginación de vehículos

También se verificó el servicio de listado de vehículos con los 11 registros:

| Consulta | Resultado |
|---|---:|
| Primera página | 10 vehículos |
| Segunda página | 1 vehículo |
| Total | 11 vehículos |
| Total de páginas | 2 |

### Protección contra duplicaciones

El seeder comprueba que las cuatro tablas estén vacías antes de insertar datos.

Si encuentra registros existentes, rechaza la operación mediante:

```text
RuntimeError:
Los datos demo requieren una base de datos completamente vacía.
```

En una comprobación anterior sobre la base de prueba persistente, se verificó que la segunda ejecución no modificara los conteos existentes:

```text
Clientes, sucursales, vehiculos, reservas: [3, 3, 11, 2]
CORRECTO: registros conservados
```

La prueba aislada de la carga ampliada y la prueba de rechazo de una segunda ejecución se realizaron por separado.

### Pendientes del seeder

- Verificar la carga después de aplicar migraciones Alembic en una base temporal.
- Documentar el procedimiento completo de preparación de la base.
- Coordinar con Piero la inicialización opcional de datos desde `app/main.py`.

## 7. Pruebas automatizadas

Se implementaron pruebas aisladas para los módulos de clientes y sucursales utilizando `unittest`, `TestClient` y una base SQLite de prueba.

La suite actual contempla:

| Módulo | Pruebas aprobadas |
|---|---:|
| Clientes | 9 |
| Sucursales | 5 |
| **Total** | **14** |

Comando ejecutado:

```bash
python -m unittest tests.test_clientes tests.test_sucursales -v
```

**Resultado: 14 pruebas aprobadas.**

Las pruebas de clientes incluyen:

- Creación y normalización del RUT.
- Listado de clientes.
- Consulta de clientes existentes.
- Respuesta 404 para clientes inexistentes.
- Respuesta 409 para RUT duplicados.
- Validación de correo electrónico.
- Rechazo de datos obligatorios faltantes.
- Distinción entre errores de unicidad y otros errores de integridad.

Las pruebas de sucursales verifican las operaciones implementadas y las validaciones correspondientes al módulo.

También se incorporó una comprobación específica para distinguir una violación UNIQUE de RUT de un error de integridad diferente.

## 8. Pruebas HTTP manuales

Archivo:

`tests_manual/clientes_sucursales.http`

Se amplió el archivo de solicitudes para REST Client de Visual Studio Code.

Actualmente contiene solicitudes para comprobar:

### Clientes

- Listado.
- Creación.
- Consulta de cliente existente.
- Consulta de cliente inexistente.
- RUT duplicado.
- Correo inválido.
- Campo adicional.
- Nombre compuesto únicamente por espacios.

### Sucursales

- Listado.
- Creación.
- Consulta de sucursal existente.
- Consulta de sucursal inexistente.
- Ciudad compuesta únicamente por espacios.
- Campo adicional.

Las solicitudes están preparadas para ejecución manual. La ampliación del archivo no se considera evidencia de que todas las solicitudes hayan sido ejecutadas y aprobadas.

## 9. Calidad del código

Se ejecutó Ruff sobre los archivos correspondientes a la responsabilidad de clientes y sucursales.

Comando utilizado:

```bash
python -m ruff check \
app/datos_demo.py \
app/repositories/clientes.py \
app/repositories/sucursales.py \
app/routers/clientes.py \
app/routers/sucursales.py \
app/schemas/clientes.py \
app/schemas/sucursal.py \
app/services/clientes.py \
app/services/sucursales.py \
tests/test_clientes.py \
tests/test_sucursales.py
```

**Resultado:**

```text
All checks passed!
```

También se ejecutó Ruff sobre el proyecto completo:

```bash
python -m ruff check app tests
```

En esa revisión se identificaron nueve observaciones en archivos compartidos y módulos de vehículos y reservas.

Estas observaciones no corresponden a los archivos de clientes y sucursales revisados individualmente.

Se ejecutó anteriormente:

```bash
git diff --check
```

Sin observaciones.

## 10. Documentación

Se dispone de los siguientes documentos:

- `docs/clientes-sucursales.md`: describe los módulos, validaciones, endpoints, persistencia y pruebas.
- `docs/diagramas.md`: representa las entidades, atributos, claves y relaciones del sistema.
- `docs/avance-gabriel.md`: registra las responsabilidades, implementaciones y evidencias de esta parte del proyecto.

Los documentos de módulos y diagramas fueron actualizados durante la revisión final para reflejar los modelos ORM y las validaciones implementadas.

## 11. Estado de Git

La rama de trabajo actual es:

`feat/parte-2-clientes-sucursales`

La rama se encontraba sincronizada con:

`origin/feat/parte-2-clientes-sucursales`

En la última revisión del historial se identificaron siete commits existentes:

1. `96e9a7a` — Adaptar esquemas a ORM.
2. `24a0068` — Implementar repositorio ORM.
3. `7123037` — Integrar servicio ORM de clientes.
4. `736ef4a` — Integrar persistencia ORM de sucursales.
5. `7800b1b` — Agregar validador de correo.
6. `431642c` — Agregar pruebas automatizadas.
7. `5476783` — Completar módulos, datos demo y documentación.

Durante la auditoría se identificaron modificaciones pendientes en archivos de implementación, pruebas y documentación.

Los cambios todavía deben revisarse y organizarse antes de preparar el commit final.

## 12. Pendientes de entrega

- [ ] Verificar el seeder después de aplicar migraciones Alembic.
- [ ] Comprobar persistencia tras reiniciar un proceso.
- [ ] Ejecutar y registrar las solicitudes HTTP manuales.
- [ ] Revisar el estado final de todos los archivos modificados.
- [ ] Revisar los nueve avisos globales de Ruff con los responsables correspondientes.
- [ ] Ejecutar las verificaciones finales del proyecto.
- [ ] Preparar el commit final de los cambios pendientes.
- [ ] Verificar la publicación de los cambios en GitHub.
- [ ] Preparar el Pull Request hacia `main`.

## 13. Estado de entrega

La implementación de los módulos de clientes y sucursales está desarrollada y cuenta con 14 pruebas automatizadas aprobadas.

Se verificaron las validaciones de entrada, la normalización del RUT, la restricción de unicidad, el manejo de conflictos de integridad y las relaciones ORM.

El seeder ampliado fue probado en SQLite en memoria, generando 17 registros relacionados correctamente y permitiendo demostrar la paginación de los 11 vehículos.

Los módulos correspondientes a la responsabilidad individual de Gabriel pasan las verificaciones de Ruff.

La documentación de módulos y diagramas fue actualizada.

La entrega individual todavía requiere completar las verificaciones finales, revisar los cambios pendientes de Git y preparar el commit y Pull Request correspondientes.

La integración general de vehículos, reservas y componentes compartidos corresponde al trabajo coordinado del equipo y de sus respectivos responsables.