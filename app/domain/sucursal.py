"""Entidad que representa una sucursal de la concesionaria."""


class Sucursal:
    def __init__(
        self,
        id: int,
        nombre: str,
        direccion: str,
        ciudad: str,
        telefono: str,
        horario_atencion: str,
    ) -> None:
        self.id = id
        self.nombre = nombre
        self.direccion = direccion
        self.ciudad = ciudad
        self.telefono = telefono
        self.horario_atencion = horario_atencion

    def a_registro(self) -> dict[str, object]:
        """Convierte la entidad al formato del almacenamiento compartido."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "direccion": self.direccion,
            "ciudad": self.ciudad,
            "telefono": self.telefono,
            "horario_atencion": self.horario_atencion,
        }