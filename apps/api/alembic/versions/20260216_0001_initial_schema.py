"""initial_schema

Revision ID: 20260216_0001
Revises:
Create Date: 2026-02-16 00:00:01
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260216_0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "breeds",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.String(length=120), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("descricao"),
    )
    op.create_index("ix_breeds_descricao", "breeds", ["descricao"], unique=False)

    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=True),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf"),
    )
    op.create_index("ix_clients_cpf", "clients", ["cpf"], unique=True)
    op.create_index("ix_clients_name", "clients", ["name"], unique=False)

    op.create_table(
        "addresses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("logradouro", sa.String(length=255), nullable=False),
        sa.Column("cidade", sa.String(length=120), nullable=False),
        sa.Column("bairro", sa.String(length=120), nullable=False),
        sa.Column("complemento", sa.String(length=255), nullable=True),
        sa.Column("tag", sa.String(length=60), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_addresses_client_id", "addresses", ["client_id"], unique=False)
    op.create_index("ix_addresses_cidade", "addresses", ["cidade"], unique=False)

    op.create_table(
        "contacts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("tag", sa.String(length=60), nullable=False),
        sa.Column(
            "tipo",
            sa.Enum("EMAIL", "TELEFONE", name="contact_type", native_enum=False),
            nullable=False,
        ),
        sa.Column("valor", sa.String(length=255), nullable=False),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_contacts_client_id", "contacts", ["client_id"], unique=False)

    op.create_table(
        "pets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=False),
        sa.Column("breed_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("birth_date", sa.Date(), nullable=False),
        sa.Column("photo_url", sa.String(length=512), nullable=True),
        sa.ForeignKeyConstraint(["breed_id"], ["breeds.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_pets_breed_id", "pets", ["breed_id"], unique=False)
    op.create_index("ix_pets_client_id", "pets", ["client_id"], unique=False)
    op.create_index("ix_pets_name", "pets", ["name"], unique=False)

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cpf", sa.String(length=14), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            sa.Enum("ADMIN", "CLIENTE", name="user_role", native_enum=False),
            nullable=False,
        ),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("client_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["client_id"], ["clients.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cpf"),
        sa.UniqueConstraint("client_id"),
    )
    op.create_index("ix_users_cpf", "users", ["cpf"], unique=False)

    op.create_table(
        "appointments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("pet_id", sa.Integer(), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("valor", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column("data", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["pet_id"], ["pets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_appointments_data", "appointments", ["data"], unique=False)
    op.create_index("ix_appointments_pet_id", "appointments", ["pet_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_appointments_pet_id", table_name="appointments")
    op.drop_index("ix_appointments_data", table_name="appointments")
    op.drop_table("appointments")

    op.drop_index("ix_users_cpf", table_name="users")
    op.drop_table("users")

    op.drop_index("ix_pets_name", table_name="pets")
    op.drop_index("ix_pets_client_id", table_name="pets")
    op.drop_index("ix_pets_breed_id", table_name="pets")
    op.drop_table("pets")

    op.drop_index("ix_contacts_client_id", table_name="contacts")
    op.drop_table("contacts")

    op.drop_index("ix_addresses_cidade", table_name="addresses")
    op.drop_index("ix_addresses_client_id", table_name="addresses")
    op.drop_table("addresses")

    op.drop_index("ix_clients_name", table_name="clients")
    op.drop_index("ix_clients_cpf", table_name="clients")
    op.drop_table("clients")

    op.drop_index("ix_breeds_descricao", table_name="breeds")
    op.drop_table("breeds")
