"""Servicio con las reglas de negocio para los clientes."""


from app.domain.cliente import Cliente
from app.errores import ErrorAplicacion
from app.repositories import clientes as respositorio_clientes


def normalizar_rut(rut: str) -> str:
    return rut.replace(".", "").replace(" ", "").upper()


def listar_clientes() -> list[dict[str, object]]:
    return respositorio_clientes.listar()


def obtener_cliente(cliente_id: int) -> dict[str, object]:
    cliente = respositorio_clientes.obtener(cliente_id)

    if cliente is None:
        raise ErrorAplicacion(
            estado_http=404,
            codigo="RESOURCE_NOT_FOUND",
            mensaje=f"No existe un cliente con ID{cliente_id}.",
            detalles=[],
        )
    return cliente


def crear_cliente(datos: dict[str, str]) -> dict[str, object]:

    rut = normalizar_rut(datos["rut"])

    if not rut:
        raise ErrorAplicacion(
            estado_http=400,
            codigo="BUSINESS_RULE_VIOLATION",
            mensaje=f"El RUT del cliente no puede estar vacio.",
            detalles=[],
        )


    for cliente in respositorio_clientes.listar():
        if cliente["rut"] == rut:
            raise ErrorAplicacion(
                estado_http=409,
                codigo="DUPLICATE_RESOURCE",
                mensaje=f"Ya existe un cliente registrado con ese RUT {rut}.",
                detalles=[]
            )


    cliente = Cliente(
        id = respositorio_clientes.asignar_id(),
        rut=rut,
        nombre=datos["nombre"],
        correo=datos["correo"],
        telefono=datos["telefono"],
        direccion=datos["direccion"],
    )

    registro = cliente.a_registro()
    respositorio_clientes.guardar(registro)


    return registro




    
