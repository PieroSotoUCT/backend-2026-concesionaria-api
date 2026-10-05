# API de concesionaria

Proyecto academico de Desarrollo de Backend. La concesionaria y sus datos
son un caso propuesto para practicar una API REST; no corresponden a una
investigacion de una empresa real.

## Estado actual

Esta es la base compartida de la Etapa 1. Solo existe `GET /health`.
Vehiculos, sucursales, clientes y reservas aun no tienen endpoints. El
contrato y el reparto acordados estan en [CONTRATO.md](CONTRATO.md), y el
avance real en [PROGRESO.md](PROGRESO.md).

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
<https://github.com/PieroSotoUCT/backend-2026-concesionaria-api>. Cuando `main`
este publicado, cada integrante puede obtenerlo y crear su propia rama:

```powershell
git clone https://github.com/PieroSotoUCT/backend-2026-concesionaria-api.git
cd backend-2026-concesionaria-api
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

Los nombres reales, el numero de grupo y la conformidad docente con un
equipo de tres personas estan pendientes de confirmar. La guia propone el
nombre `backend-2026-grupo-XX`; el nombre elegido sin numero tambien queda
pendiente de validacion academica.

## Modulo de reservas

Responsable: Roberto Gonzalez (rama `feat/reservas`). Usa las colecciones
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
$cuerpo = @{ cliente_id = 1; vehiculo_id = 3; fecha_vencimiento = "2026-10-12"; monto_reserva = 500000 } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8000/reservas -ContentType "application/json" -Body $cuerpo
Invoke-RestMethod -Method Patch -Uri http://127.0.0.1:8000/reservas/1 -ContentType "application/json" -Body '{"estado":"cancelada"}'
```

Antes de reservar deben existir un cliente y un vehiculo; mientras esos
modulos no estan integrados, se pueden cargar con los datos de demostracion
(`CONCESIONARIA_DATOS_DEMO=1`) cuando la rama de vehiculos este en `main`.

### Pruebas

```powershell
.\.venv\Scripts\python.exe -m unittest tests.test_reservas -v
```

Incluyen pruebas del servicio (disponibilidad, cancelacion, vencimiento sin
cambios parciales) y pruebas HTTP contra un servidor propio con memoria
independiente (flujo completo, errores 400/404/409 y validaciones 422).
