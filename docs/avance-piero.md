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
