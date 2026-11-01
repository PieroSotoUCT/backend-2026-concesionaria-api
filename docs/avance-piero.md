# Avance de Piero

## Etapa 1: base comun verificable

Rama `fix/base-vehiculos-integracion`, creada desde `origin/main` en
`615cc3c`. La creacion del esquema queda a cargo de Alembic; importar la API
no lo crea. La URL de migracion y API se toma de `app/db.py`, y SQLite activa
claves foraneas por conexion. `initialize_database()` se conserva sin efecto
para las llamadas heredadas de otros modulos hasta que sus responsables las
retiren. El contrato de sesion y transaccion esta en `CONTRATO.md`.

`tests/soporte_bd.py` expone `entorno_base_temporal()`. Se usa como contexto
`with entorno_base_temporal() as (entorno, ruta):`; el diccionario `entorno`
incluye `CONCESIONARIA_DATABASE_URL` y debe pasarse a todos los subprocesos.
No se importa `app.db` antes de definir la URL para la prueba. El contexto
elimina la base al terminar. `tests/test_base_piero.py` comprueba importacion,
migracion, tablas, relaciones, enforcement de FK y lectura HTTP de una fixture
ORM creada en otro proceso.

Comando desde la raiz del proyecto:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_base_piero -v
```

Resultado del 1 de noviembre de 2026: **1 prueba aprobada** (`OK`, 7.137 s)
con Python del entorno virtual. La primera ejecucion detecto un bloqueo
transitorio del archivo SQLite al limpiar el directorio temporal en Windows;
el helper ahora reintenta esa limpieza y la segunda ejecucion paso. No se
ejecuto la suite completa: las pruebas antiguas de vehiculos siguen basadas
en colecciones en memoria y las de otros responsables aun no fijan una base
temporal antes de importar `app.db`.

## Coordinacion pendiente

- Gabriel: retirar la llamada a `initialize_database()` de
  `app/services/clientes.py` y `app/services/sucursales.py` cuando actualice
  sus archivos. La funcion queda disponible mientras tanto.
- Roberto: retirar esa llamada de `app/services/reservas.py` y acordar una
  variante de procesamiento de vencimientos que reciba la sesion ORM activa.
  Piero conectara esa interfaz desde vehiculos en una etapa posterior.
- Roberto: sus pruebas de integracion ORM usan `limpiar_base()` y IDs fijos;
  deben activar una SQLite temporal antes de importar `app.db` y crear
  referencias ORM propias. No se ejecutan contra la base por defecto.

## Etapa 2: vehiculos y responsabilidades

`app/repositories/vehiculos.py` concentra `select`, filtros, ordenacion,
paginacion y `flush`. Por ejemplo, `GET /vehiculos?marca=Prueba&limite=1`
solicita al repositorio registros de esa marca y el total anterior a la
paginacion; el servicio solo construye la respuesta. Los cinco endpoints
conservan sus rutas y DTO. El mapper `_registro` de
`app/services/vehiculos.py` convierte cada modelo ORM en el diccionario de
salida; `app/domain/vehiculo.py` define los valores permitidos de estado,
condicion y transmision. Se retiro la clase de dominio antigua que duplicaba
el modelo ORM sin participar en ninguna operacion.

Vehiculos llama a `procesar_vencimientos()` del servicio de Roberto antes de
listar, consultar, actualizar y eliminar. Esa funcion publica abre su propia
transaccion antes de que vehiculos abra la suya; asi no hay una sesion anidada
ni una importacion circular. Queda pendiente acordar una variante que reciba
la sesion activa para una transaccion unica entre ambos modulos.

Prueba aislada de esta etapa:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_base_piero tests.test_vehiculos_orm -v
```

`tests/test_vehiculos_orm.py` migra su SQLite temporal, crea referencias ORM
validas y pasa la misma URL al servidor HTTP. Incluye los cinco endpoints,
filtro, orden, paginacion, vencimiento, sucursal inexistente, historial,
venta y ausencia de cambios parciales. `tests/test_vehiculos.py` conserva aun
sus fixtures de memoria; su migracion completa corresponde a la etapa 3.
Resultado del 1 de noviembre de 2026: **2 pruebas aprobadas** (`OK`, 12.397 s)
con el comando anterior. La suite completa no se ejecuto por los fixtures
antiguos de memoria y por la falta de aislamiento previo en pruebas ajenas.

## Etapa 3: pruebas y evidencia de vehiculos

`tests/test_vehiculos.py` conserva sus 15 casos. Ahora migra una SQLite
temporal y prepara sucursales, cliente, 12 vehiculos y reservas mediante ORM,
sin asumir los IDs del seeder. Los tres casos de reglas directas usan bases
temporales propias y verifican los efectos con nuevas sesiones. Ningun test
importa `app.db` antes de definir `CONCESIONARIA_DATABASE_URL` en el proceso
que lo usa. El servidor HTTP hereda la misma URL que las fixtures.

La revision nueva `20261101_ids_sin_reuso` reconstruye las cuatro tablas de
SQLite con `AUTOINCREMENT`, conservando los registros y relaciones existentes.
No modifica la revision compartida `20261028_orm`. La prueba de migracion
actualiza una base con datos de las cuatro entidades, comprueba sus relaciones
y confirma que el ID mayor eliminado no se reutiliza en ninguna tabla. Una
base antigua que ya haya eliminado IDs antes de esta revision no conserva
informacion suficiente para reconstruir esos valores historicos.
Tambien se comprobo `downgrade` a `20261028_orm` seguido de una nueva subida
a `head`, conservando registros y relaciones (`OK`, 10.349 s en la prueba
focalizada).

`tests_manual/vehiculos.http` indica comandos para una base de prueba nueva,
usa los tres vehiculos reales del seeder y los IDs 4 y 5 para sus creaciones.
Se comprobaron sus 33 solicitudes en orden contra una SQLite temporal con
Uvicorn y datos demo; todos los codigos HTTP obtenidos coincidieron con los
esperados. No se uso `concesionaria.db`.

Comandos para repetir las pruebas propias:

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_base_piero tests.test_vehiculos tests.test_vehiculos_orm -v
```

Resultado del 1 de noviembre de 2026: **18 pruebas propias aprobadas**
(`OK`, 35.588 s, antes de agregar la comprobacion de downgrade indicada
arriba). Pyright informo 0 errores y 0 advertencias en los tres
archivos de pruebas. `git diff --check` paso y no se creo `concesionaria.db`.
La suite de Gabriel y Roberto no se ejecuto porque sus pruebas aun deben
aislar la URL antes de importar `app.db`.

La comprobacion de vencimientos en vehiculos ya se ejecuta contra la interfaz
publica de Roberto. Queda pendiente que Roberto exponga una variante con la
sesion activa para una transaccion unica y que adapte sus pruebas aisladas.

## Etapa 4: integracion y documentacion

Se revisaron los PR #3 de Gabriel y #4 de Roberto en GitHub: ambos ya estaban
fusionados en `main` (`3284e81` y `615cc3c`). El #3 agrego las rutas y
pruebas de clientes y sucursales; el #4 agrego ORM, migracion y dos pruebas
de integracion. No se fusiono ningun PR en esta etapa. El README,
`CONTRATO.md` y `PROGRESO.md` se corrigieron segun el codigo actual.
Se importo la API con una URL de SQLite temporal y se genero OpenAPI:
15 operaciones de negocio en ocho rutas, mas `GET /health`. No se creo la
base al importar.

Para reproducir los fallos ajenos se creo una SQLite temporal distinta por
modulo, se aplico `alembic upgrade head` y se ejecuto cada modulo con esa
URL heredada por el subproceso. Resultados del 1 de noviembre de 2026:

Desde la raiz, este comando reproduce un modulo sin tocar la base local;
cambia `tests.test_clientes` por otro de la tabla cuando corresponda:

```powershell
@'
import subprocess, sys
from tests.soporte_bd import entorno_base_temporal
with entorno_base_temporal() as (entorno, _ruta):
    subprocess.run([sys.executable, '-m', 'alembic', 'upgrade', 'head'],
                   env=entorno, check=True)
    subprocess.run([sys.executable, '-m', 'unittest',
                    'tests.test_clientes', '-v'], env=entorno)
'@ | .\.venv\Scripts\python.exe -
```

| Modulo | Resultado | Caso y responsable |
| --- | --- | --- |
| `tests.test_clientes` | 4 tests, 5 errores | `tests/test_clientes.py` usa `datos.vehiculos` inexistente y su servidor termina antes de iniciar. Gabriel. |
| `tests.test_sucursales` | 4 tests, 5 errores | `tests/test_sucursales.py` usa `datos.vehiculos` inexistente y su servidor termina antes de iniciar. Gabriel. |
| `tests.test_reservas` | 12 tests, 13 errores | `tests/test_reservas.py` usa `datos.vehiculos` inexistente y su servidor termina antes de iniciar. Roberto. |
| `tests.test_orm_integracion` | 2 tests, 1 error | `tests/test_orm_integracion.py` presupone `cliente_id=1` despues de limpiar registros; `crear_reserva` devuelve 404 porque SQLite ya asigno otro ID. Roberto. |

`app/services/clientes.py` y `app/services/sucursales.py` aun tienen `select`
y acceso ORM directo; `app/repositories/clientes.py` y
`app/repositories/sucursales.py` siguen implementados sobre diccionarios que
ya no existen. Gabriel debe trasladar las consultas conservando sus rutas y
respuestas. `app/datos_demo.py` crea un solo cliente, no los dos requeridos.

No se encontraron `docs/diagramas.md` (Gabriel) ni
`docs/evidencias-pruebas.md` (Roberto) en `origin/main` ni en esta rama.
Se necesitan el diagrama de clases y datos y seis casos con entrada, esperado
y obtenido; la prueba de persistencia debe parar e iniciar de nuevo Uvicorn
sin recargar el seeder. Estas tareas siguen con sus responsables y no se
marcan completas.
