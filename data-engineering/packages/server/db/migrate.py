from pathlib import Path

from alembic import command
from alembic.config import Config

ALEMBIC_INI = Path(__file__).resolve().parents[3] / "alembic.ini"


# Alembic records applied revisions in an `alembic_version` table, so boot is
# safe against a persisted database — each migration's upgrade() runs exactly
# once, ever.
def migrate() -> None:
    command.upgrade(Config(str(ALEMBIC_INI)), "head")
