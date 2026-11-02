"""Entorno de SQLite temporal para procesos de prueba independientes."""

import os
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from collections.abc import Iterator


@contextmanager
def entorno_base_temporal() -> Iterator[tuple[dict[str, str], Path]]:
    """Entrega entorno y ruta; pasarlos a migracion, fixtures y servidor."""
    temporal = tempfile.TemporaryDirectory(prefix="concesionaria-test-")
    try:
        ruta = Path(temporal.name) / "pruebas.db"
        entorno = os.environ.copy()
        entorno["CONCESIONARIA_DATABASE_URL"] = f"sqlite:///{ruta.as_posix()}"
        entorno.pop("CONCESIONARIA_DATOS_DEMO", None)
        yield entorno, ruta
    finally:
        for intento in range(10):
            try:
                temporal.cleanup()
                break
            except PermissionError:
                if intento == 9:
                    raise
                time.sleep(0.2)
