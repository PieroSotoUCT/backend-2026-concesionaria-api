"""Gestiona los clientes de la consecionaria."""


from app.repositories import datos


def asignar_id() -> int:
    return datos.siguiente_id("clientes")


def listar() ->list[dict[str, object]]:
    return[dict(registro) for registro in datos.clientes.values()]


def obtener(cliente_id: int) -> dict[str, object] | None:
    registro = datos.clientes.get(cliente_id)
    return dict(registro) if registro is not None else None


def guardar(registro: dict[str, object]) -> None:
    datos.clientes[registro["id"]] = dict(registro)
