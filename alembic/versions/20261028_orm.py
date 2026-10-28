"""Create concessionaria ORM tables."""

from alembic import op
import sqlalchemy as sa

revision = "20261028_orm"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sucursales",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("direccion", sa.String(200), nullable=False),
        sa.Column("ciudad", sa.String(100), nullable=False),
        sa.Column("telefono", sa.String(30), nullable=False),
        sa.Column("horario_atencion", sa.String(120), nullable=False),
    )
    op.create_table(
        "clientes",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("rut", sa.String(20), nullable=False, unique=True),
        sa.Column("nombre", sa.String(100), nullable=False),
        sa.Column("correo", sa.String(254), nullable=False),
        sa.Column("telefono", sa.String(30), nullable=False),
        sa.Column("direccion", sa.String(200), nullable=False),
    )
    op.create_table(
        "vehiculos",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("marca", sa.String(50), nullable=False),
        sa.Column("modelo", sa.String(50), nullable=False),
        sa.Column("anio", sa.Integer(), nullable=False),
        sa.Column("precio", sa.Integer(), nullable=False),
        sa.Column("kilometraje", sa.Integer(), nullable=False),
        sa.Column("transmision", sa.String(20), nullable=False),
        sa.Column("condicion", sa.String(20), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
        sa.Column("sucursal_id", sa.Integer(), sa.ForeignKey("sucursales.id"), nullable=False),
    )
    op.create_table(
        "reservas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cliente_id", sa.Integer(), sa.ForeignKey("clientes.id"), nullable=False),
        sa.Column("vehiculo_id", sa.Integer(), sa.ForeignKey("vehiculos.id"), nullable=False),
        sa.Column("fecha_reserva", sa.Date(), nullable=False),
        sa.Column("fecha_vencimiento", sa.Date(), nullable=False),
        sa.Column("monto_reserva", sa.Integer(), nullable=False),
        sa.Column("estado", sa.String(20), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("reservas")
    op.drop_table("vehiculos")
    op.drop_table("clientes")
    op.drop_table("sucursales")
