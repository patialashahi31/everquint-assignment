import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import all models so Alembic can detect them for autogenerate
from app.models.base import Base
from app.models.room import Room
from app.models.booking import Booking
from app.models.idempotency import IdempotencyKey

# Alembic Config object
config = context.config

# Override sqlalchemy.url from environment variable
# This means no DB credentials ever hardcoded in alembic.ini
config.set_main_option("sqlalchemy.url", os.environ["DATABASE_URL"])

# Setup logging from alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is what alembic uses to autogenerate migrations
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()