"""users

Revision ID: 0001
Revises:
Create Date: 2026-08-31 09:39:05.930440

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# `availability` is stored as a JSON-encoded text column.
# In production this would be a Postgres jsonb; SQLite has no jsonb type,
# so the resolvers parse/stringify at the boundary.
def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.Text(), primary_key=True),
        sa.Column("firstName", sa.Text(), nullable=False),
        sa.Column("lastName", sa.Text(), nullable=False),
        sa.Column("phoneNumber", sa.Text(), nullable=False),
        sa.Column("availability", sa.Text(), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("users")
