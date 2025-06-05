"""add clicks column to urls

Revision ID: db65a650cb9d
Revises: 57a9669ee3e5
Create Date: 2025-06-02 16:01:26.216722
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "db65a650cb9d"
down_revision: Union[str, None] = "57a9669ee3e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """SQLite-safe upgrade."""
    with op.batch_alter_table("urls", recreate="always") as batch_op:
        batch_op.add_column(
            sa.Column("clicks", sa.Integer(), nullable=False, server_default="0")
        )
        batch_op.alter_column("short_code", nullable=False)


def downgrade() -> None:
    """SQLite-safe downgrade."""
    with op.batch_alter_table("urls", recreate="always") as batch_op:
        batch_op.drop_column("clicks")
        batch_op.alter_column("short_code", nullable=True)

