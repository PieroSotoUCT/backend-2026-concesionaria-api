"""Entidad que representa a un cliente de la concesionaria."""

class Cliente:
    def __init__(
        self,
        id: int,
        rut: str,
        nombre: str,
        correo: str,
        telefono: str,
        direccion: str,
    ) -> None:
        self.id = id
        self.rut = rut
        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono
        self.direccion = direccion

    
    def a_registro(self) ->dict[str, object]:
        return {
            "id": self.id,
            "rut": self.rut,
            "nombre": self.correo,
            "telefono": self.telefono,
            "direccion": self.direccion,
        }
        