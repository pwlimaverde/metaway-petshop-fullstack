"""client_cpf_and_multi_users_per_client

Revision ID: 93d947f1ce4c
Revises: bad35038006e
Create Date: 2026-02-16 19:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "93d947f1ce4c"
down_revision: str | Sequence[str] | None = "20260216_0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column("clients", sa.Column("cpf", sa.String(length=14), nullable=True))
    op.create_unique_constraint("uq_clients_cpf", "clients", ["cpf"])

    op.execute(
        sa.text(
            """
            UPDATE clients
            SET cpf = users.cpf
            FROM users
            WHERE users.client_id = clients.id
              AND clients.cpf IS NULL
            """
        )
    )

    op.drop_constraint("users_client_id_key", "users", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("users_client_id_key", "users", ["client_id"])
    op.drop_constraint("uq_clients_cpf", "clients", type_="unique")
    op.drop_column("clients", "cpf")
