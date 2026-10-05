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
