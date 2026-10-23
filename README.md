# API de concesionaria

Proyecto academico de Desarrollo de Backend. En este caso propuesto, el
personal de ventas y los encargados de sucursal registran inventario y
reservas en planillas o mensajes separados. Esto dificulta conocer la
disponibilidad y puede producir reservas duplicadas. La concesionaria y sus
datos no corresponden a una investigacion de una empresa real.

## Estado actual

Las etapas 1 a 5 completan los cinco endpoints de vehiculos, sus reglas y las
consultas con filtros, ordenamiento y paginacion en `feat/vehiculos`.
El PR #1 hacia `main` esta abierto; `main` contiene la base compartida y
reservas.
Roberto integro reservas en `main` mediante el PR #2. Esta rama local ya
incluye ambos modulos. Clientes y sucursales siguen a cargo de Gabriel.
`GET /health` permite comprobar el proceso.
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

## Contrato de endpoints y estado actual

| Metodo y ruta | Funcion | Exito | Estado |
| --- | --- | --- | --- |
| `POST /vehiculos` | Crear en una sucursal existente | 201 | Implementado por Piero |
| `GET /vehiculos` | Listar con filtros, orden y paginacion | 200 | Implementado por Piero |
| `GET /vehiculos/{id}` | Obtener por ID | 200 | Implementado por Piero |
| `PATCH /vehiculos/{id}` | Actualizar campos enviados | 200 | Implementado por Piero |
| `DELETE /vehiculos/{id}` | Eliminar sin historial de reservas | 204 | Implementado por Piero |
| `POST /sucursales` | Crear sucursal | 201 | Pendiente: Gabriel |
| `GET /sucursales` | Listar sucursales | 200 | Pendiente: Gabriel |
| `GET /sucursales/{id}` | Obtener sucursal por ID | 200 | Pendiente: Gabriel |
| `POST /clientes` | Crear cliente con RUT unico | 201 | Pendiente: Gabriel |
| `GET /clientes` | Listar clientes | 200 | Pendiente: Gabriel |
| `GET /clientes/{id}` | Obtener cliente por ID | 200 | Pendiente: Gabriel |
| `POST /reservas` | Reservar vehiculo disponible | 201 | Implementado por Roberto |
| `GET /reservas` | Listar reservas | 200 | Implementado por Roberto |
| `GET /reservas/{id}` | Obtener reserva por ID | 200 | Implementado por Roberto |
| `PATCH /reservas/{id}` | Cancelar reserva activa | 200 | Implementado por Roberto |

`GET /health` comprueba el proceso y no cuenta entre los 15 endpoints de
negocio acordados. En esta rama Swagger muestra los cinco de vehiculos,
los cuatro de reservas y `/health`; faltan las seis rutas de Gabriel.
Los errores de vehiculos incluyen 400 por regla de estado, 404 por recurso o
sucursal inexistente, 409 por conflicto e historial, y 422 por datos o
parametros invalidos. Todos los errores controlados usan el formato de
`CONTRATO.md`. Los DTO, parametros, ejemplos y respuestas de las rutas
implementadas se pueden consultar en Swagger.
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

### Demostracion breve en Swagger

Inicia el servidor con datos de demostracion y abre `/docs`. Desde una
instancia nueva, ejecuta estas cuatro operaciones en orden:

1. `POST /vehiculos` con el cuerpo siguiente: responde 201 e ID 13.
2. `GET /vehiculos/13`: responde 200 con el vehiculo creado.
3. `PATCH /vehiculos/999` con `{"precio":12000000}`: responde 404 con el
   formato de error comun.
4. `GET /vehiculos?marca=toyota&estado=disponible&sucursal_id=1&precio_min=10000000&precio_max=26000000&ordenar_por=precio&direccion=desc&pagina=1&limite=1`:
   responde 200 con el vehiculo 9, `total=2` y `total_paginas=2`.

```json
{"marca":"Honda","modelo":"Civic","anio":2022,"precio":15000000,"kilometraje":12000,"transmision":"manual","condicion":"usado","sucursal_id":1}
```

Las cuatro operaciones muestran dos casos exitosos, un error y una coleccion
con filtro, orden y paginacion. Reinicia el servidor con ejemplos antes de
repetir la demostracion.

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
Reservas ya revisa vencimientos antes de sus propias operaciones; falta
conectarlo con las consultas y operaciones de vehiculos. Las pruebas completas
entre modulos siguen pendientes de la integracion del equipo.

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
la base comun y reservas. Para obtener la implementacion de Piero:

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

Las cinco areas de seguimiento de la guia quedan distribuidas asi:
coordinacion y API/logica de negocio, Piero; dominio y datos, Gabriel;
calidad y pruebas, Roberto; documentacion e integracion, Piero y Gabriel
con aportes de los tres. Cada integrante desarrolla, prueba y documenta
su modulo, y todos deben comprender la API completa para la defensa.

El numero de grupo y la conformidad docente con un equipo de tres personas
estan pendientes de confirmar. La guia propone el nombre
`backend-2026-grupo-XX`; el nombre elegido sin numero tambien queda pendiente
de validacion academica.

## Modulo de reservas

Responsable: Roberto Gonzalez (PR #2). Usa las colecciones
compartidas de `app/repositories/datos.py` y sigue [CONTRATO.md](CONTRATO.md).

| Metodo y ruta | Proposito | Respuestas |
| --- | --- | --- |
| `POST /reservas` | Reservar un vehiculo disponible | 201, 400, 404, 409, 422 |
| `GET /reservas` | Listar todas las reservas por ID ascendente | 200 |
| `GET /reservas/{id}` | Consultar una reserva | 200, 404, 422 |
| `PATCH /reservas/{id}` | Cancelar: solo acepta `{"estado":"cancelada"}` | 200, 404, 409, 422 |

Campos de entrada de `POST /reservas`: `cliente_id`, `vehiculo_id`,
`fecha_vencimiento` (`AAAA-MM-DD`) y `monto_reserva` (entero en pesos). El
servidor asigna `id`, `fecha_reserva` (`date.today()`) y `estado` (`activa`);
enviarlos da 422, igual que cualquier campo adicional.

### Reglas

- **Crear:** el cliente y el vehiculo deben existir (404). La fecha de
  vencimiento no puede ser anterior a hoy (400 `INVALID_EXPIRATION_DATE`);
  hoy mismo es valido. El vehiculo debe estar `disponible` (409
  `VEHICLE_NOT_AVAILABLE`) y pasa a `reservado`.
- **Cancelar:** solo una reserva `activa` (409 `STATE_CONFLICT` si ya esta
  cancelada o vencida). El vehiculo vuelve a `disponible`.
- **Vencer:** una reserva activa vence cuando `fecha_vencimiento < date.today()`.
  Pasa a `vencida` y su vehiculo vuelve a `disponible`. La funcion
  `procesar_vencimientos()` de `app/services/reservas.py` hace esta revision y
  devuelve cuantas reservas vencio; se ejecuta sola antes de crear, listar,
  consultar y cancelar reservas. Los vehiculos `vendido` nunca se liberan.
- Un error no deja cambios parciales: todas las comprobaciones ocurren antes
  de escribir la reserva y el estado del vehiculo.

Todos los errores usan el formato comun
`{"error":{"code":"...","message":"...","details":[]}}`.

### Ejemplo en PowerShell

```powershell
$vence = (Get-Date).AddDays(7).ToString("yyyy-MM-dd")
$cuerpo = @{ cliente_id = 1; vehiculo_id = 1; fecha_vencimiento = $vence; monto_reserva = 500000 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/reservas -ContentType "application/json" -Body $cuerpo
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/reservas/3 -ContentType "application/json" -Body '{"estado":"cancelada"}'
```

Antes de reservar deben existir un cliente y un vehiculo. En esta rama se
pueden cargar con los datos de demostracion (`CONCESIONARIA_DATOS_DEMO=1`).
El ejemplo requiere iniciar con memoria nueva: ya existen dos reservas de
demostracion, por lo que la nueva recibe ID 3 y el vehiculo 1 queda libre
despues de cancelarla.

### Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_reservas -v
```

Incluyen pruebas del servicio (disponibilidad, cancelacion, vencimiento sin
cambios parciales) y pruebas HTTP contra un servidor propio con memoria
independiente (flujo completo, errores 400/404/409 y validaciones 422).
