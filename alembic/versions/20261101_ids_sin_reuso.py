"""Evita reutilizar IDs en SQLite sin perder datos existentes."""

from alembic import op


revision = "20261101_ids_sin_reuso"
down_revision = "20261028_orm"
branch_labels = None
depends_on = None


def _recrear(sqlite_autoincrement: bool) -> None:
    conexion = op.get_bind()
    if conexion.dialect.name != "sqlite":
        return

    # SQLite necesita desactivar FK antes de recrear tablas referenciadas.
    conexion.exec_driver_sql("PRAGMA foreign_keys=OFF")
    if conexion.exec_driver_sql("PRAGMA foreign_keys").scalar() != 0:
        raise RuntimeError("No se pudo desactivar foreign_keys para la migracion")
    try:
        for tabla in ("reservas", "vehiculos", "clientes", "sucursales"):
            with op.batch_alter_table(
                tabla, recreate="always",
                table_kwargs={"sqlite_autoincrement": sqlite_autoincrement},
            ):
                pass
    except BaseException:
        conexion.rollback()
        raise
    else:
        conexion.commit()
    finally:
        conexion.exec_driver_sql("PRAGMA foreign_keys=ON")
    if conexion.exec_driver_sql("PRAGMA foreign_keys").scalar() != 1:
        raise RuntimeError("No se pudo reactivar foreign_keys tras la migracion")


def upgrade() -> None:
    _recrear(True)


def downgrade() -> None:
    _recrear(False)
