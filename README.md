# API de concesionaria

Proyecto academico de Desarrollo de Backend. La concesionaria y sus datos
son un caso propuesto para practicar una API REST; no corresponden a una
investigacion de una empresa real.

## Estado actual

La Etapa 4 completa los cinco endpoints de vehiculos, sus reglas y las consultas
con filtros, ordenamiento y paginacion en `feat/vehiculos`.
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
| `GET /vehiculos` | 200, items y metadatos de paginacion | 422 parametros invalidos |
| `GET /vehiculos/{id}` | 200, vehiculo | 404 inexistente; 422 ID invalido |
| `PATCH /vehiculos/{id}` | 200, vehiculo actualizado parcialmente | 400 estado manual; 404 recurso; 409 conflicto; 422 datos |
| `DELETE /vehiculos/{id}` | 204 sin cuerpo | 404 inexistente; 409 historial; 422 ID invalido |

Los ejemplos y las respuestas de cada operacion se pueden consultar en Swagger.
Sin datos demo ni sucursales cargadas, crear un vehiculo responde 404.

Una consulta completa sobre los ejemplos iniciales:

```http
GET /vehiculos?marca=toyota&estado=disponible&sucursal_id=1&precio_min=10000000&precio_max=26000000&ordenar_por=precio&direccion=desc&pagina=1&limite=1
```

Devuelve el vehiculo 9, `total=2` y `total_paginas=2`; la pagina 2 contiene
el vehiculo 1. Siempre se filtra primero, luego se ordena y al final se pagina.

| Parametro | Regla |
| --- | --- |
| `marca` | Coincidencia exacta, sin distinguir mayusculas ni espacios exteriores |
| `estado` | disponible, reservado o vendido |
| `sucursal_id` | Entero positivo; una sucursal sin coincidencias devuelve items vacio |
| `precio_min`, `precio_max` | Enteros desde 0, limites inclusivos; minimo no mayor que maximo |
| `ordenar_por` | precio, anio o kilometraje; si se omite, ID ascendente |
| `direccion` | asc o desc; por defecto asc; se aplica al campo elegido |
| `pagina` | Entero desde 1; por defecto 1 |
| `limite` | Entero de 1 a 100; por defecto 10 |

Los empates se resuelven por ID ascendente. La respuesta contiene `items`,
`total`, `pagina`, `limite` y `total_paginas`. Sin coincidencias devuelve
total y total_paginas en 0. Una pagina posterior al final conserva los
totales y devuelve items vacio. Parametros desconocidos o invalidos devuelven 422.

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

Tambien prueban las combinaciones de filtros, los tres campos de orden,
ambas direcciones, los empates, las paginas fuera de rango y los limites.
Para la prueba manual, abre `tests_manual/vehiculos.http` en un cliente
compatible con archivos HTTP y variables `@baseUrl`, o copia las solicitudes
a Swagger. Reinicia con ejemplos antes de ejecutar el archivo en orden:
indica los codigos y resultados esperados y utiliza los IDs nuevos 13 y 14.
Las solicitudes de ese archivo modifican datos, por lo que una segunda
demostracion debe comenzar reiniciando el servidor.

## Validaciones y reglas del modulo

| Validacion de datos (422) | Ejemplo rechazado |
| --- | --- |
| Marca y modelo: 2 a 50 caracteres | marca de un caracter |
| Anio: entero entre 1900 y 2100 | 1899 |
| Precio: entero positivo | 0 o 12.5 |
| Kilometraje: entero no negativo | -1 |
| Transmision y condicion enumeradas | transmision otra |
| Creacion sin ID ni estado del servidor | estado vendido enviado en POST |
| PATCH sin null, ID, campos extras ni cuerpo vacio | precio null |
| Parametros de consulta validos | pagina 0, limite 101 o rango invertido |

Las reglas de negocio se comprueban en el servicio: la sucursal debe existir
(404); reservar o liberar manualmente esta prohibido (400); vender exige
disponibilidad y ausencia de reserva activa (409 si no se cumple); eliminar
exige ausencia de cualquier historial de reservas (409 si existe). El estado
vendido es final. Las comprobaciones ocurren antes de guardar para que un
error no cambie parcialmente el registro.

El router recibe HTTP y devuelve respuestas documentadas. Los DTO validan
la forma de los datos. El servicio aplica esas reglas y usa el repositorio
para consultar o guardar en las colecciones comunes. La entidad Vehiculo
representa los atributos del dominio. No hay llamadas HTTP entre modulos.

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
<https://github.com/PieroSotoUCT/backend-2026-concesionaria-api>. `main` contiene
la base comun. Para obtener la implementacion de Piero:

```powershell
git clone https://github.com/PieroSotoUCT/backend-2026-concesionaria-api.git
cd backend-2026-concesionaria-api
git switch feat/vehiculos
```

Gabriel crea `feat/clientes-sucursales` y Roberto crea `feat/reservas` desde
`main`, usando `git switch main` y despues `git switch -c nombre-de-su-rama`.
Cada persona debe configurar su propia identidad
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
