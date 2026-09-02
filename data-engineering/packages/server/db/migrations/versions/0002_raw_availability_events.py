"""raw_availability_events

Revision ID: 0002
Revises: 0001
Create Date: 2026-09-02 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: str | Sequence[str] | None = "0001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


# Staging log for partner availability feeds ingested by `server.etl`. Rows
# are never deleted or overwritten by the pipeline, only appended and marked
# loaded/rejected — the idempotency guarantee for re-ingestion lives in the
# `users` upsert (keyed by phone number), not in this table.
def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "raw_availability_events",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("source", sa.Text(), nullable=False),
        sa.Column("first_name", sa.Text(), nullable=True),
        sa.Column("last_name", sa.Text(), nullable=True),
        sa.Column("phone_number", sa.Text(), nullable=True),
        sa.Column("availability_raw", sa.Text(), nullable=False),
        sa.Column("raw_payload", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False, server_default="pending"),
        sa.Column("error", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("raw_availability_events")
