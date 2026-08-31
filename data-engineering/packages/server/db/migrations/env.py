from logging.config import fileConfig

from alembic import context

from server.db.engine import engine
from server.db.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_online() -> None:
    with engine.connect() as connection:
        # SQLite cannot ALTER a column in place. Batch mode rewrites the table
        # instead, so op.batch_alter_table works on a populated database.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
