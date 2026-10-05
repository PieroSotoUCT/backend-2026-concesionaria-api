# API de concesionaria

Proyecto academico de Desarrollo de Backend. La concesionaria y sus datos
son un caso propuesto para practicar una API REST; no corresponden a una
investigacion de una empresa real.

## Estado actual

La Etapa 3 incorpora los cinco endpoints de vehiculos y sus reglas de negocio.
`GET /health` permite comprobar el proceso. Clientes, sucursales y reservas
siguen pendientes de los aportes de Gabriel y Roberto.
El contrato y el reparto acordados estan en [CONTRATO.md](CONTRATO.md), y
el avance real en [PROGRESO.md](PROGRESO.md).

## Instalacion en Windows PowerShell

Desde la raiz del proyecto, con Python 3.10 o posterior:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Ejecucion y comprobacion

Inicia un solo servidor desde la raiz:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

En otra ventana de PowerShell:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
```

Debe responder `{"estado":"ok"}`. Swagger esta en
<http://127.0.0.1:8000/docs>.

Los datos se guardan exclusivamente en memoria y se pierden al detener el
servidor. Para esta version academica se ejecuta un solo proceso servidor;
no uses varios workers porque cada proceso tendria sus propias colecciones.
No se necesitan base de datos, credenciales ni servicios externos.

## Datos de demostracion opcionales

Para iniciar con ejemplos ficticios, detiene primero el servidor anterior y
ejecuta en PowerShell:

```powershell
$env:CONCESIONARIA_DATOS_DEMO = "1"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Se cargan dos sucursales, un cliente ficticio, doce vehiculos y dos reservas
de ejemplo. El vehiculo 1 no tiene historial, el 2 tiene una reserva
cancelada, el 3 tiene una reserva activa y el 8 esta vendido. Sirven para
probar el modulo de vehiculos; no sustituyen
las pruebas de los modulos de los companeros. Para repetir desde cero,
detiene el servidor y ejecuta el mismo comando otra vez. La carga solo
funciona con memoria vacia y nunca reemplaza registros existentes. Para
iniciar sin ejemplos, quita la variable en esa ventana con
`Remove-Item Env:CONCESIONARIA_DATOS_DEMO` antes de iniciar el servidor.

## Endpoints implementados y pruebas

| Metodo y ruta | Resultado correcto | Errores controlados |
| --- | --- | --- |
| `POST /vehiculos` | 201, vehiculo disponible con ID nuevo | 404 sucursal; 422 datos |
| `GET /vehiculos` | 200, lista completa por ID | Sin parametros en esta etapa |
| `GET /vehiculos/{id}` | 200, vehiculo | 404 inexistente; 422 ID invalido |
| `PATCH /vehiculos/{id}` | 200, vehiculo actualizado parcialmente | 400 estado manual; 404 recurso; 409 conflicto; 422 datos |
| `DELETE /vehiculos/{id}` | 204 sin cuerpo | 404 inexistente; 409 historial; 422 ID invalido |

En la Etapa 3 el listado es un arreglo JSON. La Etapa 4 incorporara los
filtros, el ordenamiento y la respuesta paginada acordada en el contrato.
Los ejemplos y las respuestas de cada operacion se pueden consultar en Swagger.
Sin datos demo ni sucursales cargadas, crear un vehiculo responde 404.

Para repetir las pruebas desde la raiz, sin iniciar un servidor manualmente:

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Las pruebas crean un servidor temporal con ejemplos y lo cierran al terminar.
Cubren CRUD, IDs sin reutilizacion, PATCH parcial y errores 400/404/409/422.
Comprueban que un error no aplique cambios parciales, que las referencias
existan, que no se pueda liberar o vender un reservado y que el historial
impida eliminar. Los casos de estado incoherente y reserva vencida se
preparan directamente en memoria: no simulan endpoints de reservas.
La revision automatica de vencimientos y las pruebas entre modulos siguen
pendientes de la integracion del equipo.

## Estructura

| Ruta | Responsabilidad |
| --- | --- |
| `app/main.py` | Configuracion, routers disponibles y errores HTTP |
| `app/routers/` | Entrada HTTP |
| `app/schemas/` | DTO y validaciones de datos |
| `app/domain/` | Entidades y enumeraciones |
| `app/services/` | Reglas de negocio |
| `app/repositories/` | Colecciones en memoria y consultas |

## Trabajo en GitHub

El repositorio publico compartido es
<https://github.com/PieroSotoUCT/backend-2026-concesionaria>. Cuando `main`
este publicado, cada integrante puede obtenerlo y crear su propia rama:

```powershell
git clone https://github.com/PieroSotoUCT/backend-2026-concesionaria.git
cd backend-2026-concesionaria
git switch -c feat/vehiculos
```

Para los otros modulos se usan `feat/clientes-sucursales` y `feat/reservas`
en lugar de `feat/vehiculos`. Cada persona debe configurar su propia identidad
de Git, realizar al menos cinco commits propios y significativos, publicar
su rama y abrir un PR hacia `main`. Antes de integrar, el grupo revisa el
codigo, las pruebas del modulo y la compatibilidad con `CONTRATO.md`.
Tras hacer commits en su rama, cada integrante la publica, por ejemplo con
`git push -u origin feat/vehiculos`, y abre el PR en GitHub. Para subir ramas
al mismo repositorio, el propietario debe conceder acceso de colaborador a
las cuentas de sus companeros; un repositorio publico solo permite clonar
sin ese permiso.

## Equipo

| Integrante | Modulo principal | Seguimiento principal |
| --- | --- | --- |
| Piero Soto | Base compartida y vehiculos | Coordinacion, API e integracion |
| Gabriel Rivas | Clientes y sucursales | Dominio, datos y documentacion |
| Roberto Gonzalez | Reservas | Calidad y pruebas del conjunto |

El numero de grupo y la conformidad docente con un equipo de tres personas
estan pendientes de confirmar. La guia propone el nombre
`backend-2026-grupo-XX`; el nombre elegido sin numero tambien queda pendiente
de validacion academica.
