"""Formato compartido de los errores controlados."""


class ErrorAplicacion(Exception):
    def __init__(
        self,
        estado_http: int,
        codigo: str,
        mensaje: str,
        detalles: list[dict[str, str]] | None = None,
    ) -> None:
        self.estado_http = estado_http
        self.codigo = codigo
        self.mensaje = mensaje
        self.detalles = detalles if detalles is not None else []
        super().__init__(mensaje)


def cuerpo_error(
    codigo: str, mensaje: str, detalles: list[dict[str, str]] | None = None
) -> dict[str, object]:
    return {
        "error": {
            "code": codigo,
            "message": mensaje,
            "details": detalles if detalles is not None else [],
        }
    }
