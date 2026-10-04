"""Configuracion de FastAPI y manejo comun de errores."""

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.errores import ErrorAplicacion, cuerpo_error

app = FastAPI(
    title="API de concesionaria",
    description="Proyecto academico con almacenamiento en memoria. Modulos en desarrollo.",
    version="0.1.0",
)


def manejar_error_aplicacion(_solicitud: Request, error: ErrorAplicacion) -> JSONResponse:
    return JSONResponse(
        status_code=error.estado_http,
        content=cuerpo_error(error.codigo, error.mensaje, error.detalles),
    )


def manejar_validacion(_solicitud: Request, error: RequestValidationError) -> JSONResponse:
    detalles = [
        {
            "campo": ".".join(str(parte) for parte in fallo["loc"]),
            "mensaje": fallo["msg"],
        }
        for fallo in error.errors()
    ]
    return JSONResponse(
        status_code=422,
        content=cuerpo_error("VALIDATION_ERROR", "Datos o parametros invalidos", detalles),
    )


def manejar_http(_solicitud: Request, error: StarletteHTTPException) -> JSONResponse:
    if error.status_code == 404:
        codigo, mensaje = "RESOURCE_NOT_FOUND", "Ruta no encontrada"
    elif error.status_code == 405:
        codigo, mensaje = "METHOD_NOT_ALLOWED", "Metodo no permitido"
    else:
        codigo, mensaje = "HTTP_ERROR", str(error.detail)
    return JSONResponse(
        status_code=error.status_code,
        content=cuerpo_error(codigo, mensaje),
        headers=error.headers,
    )


app.add_exception_handler(ErrorAplicacion, manejar_error_aplicacion)
app.add_exception_handler(RequestValidationError, manejar_validacion)
app.add_exception_handler(StarletteHTTPException, manejar_http)


@app.get(
    "/health",
    summary="Comprobar que la API esta activa",
    description="Devuelve el estado del proceso. No cuenta como endpoint de negocio.",
    response_description="Estado de la aplicacion",
)
def consultar_salud() -> dict[str, str]:
    return {"estado": "ok"}
