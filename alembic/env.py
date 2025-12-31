"""Alembic environment configuration for async SQLAlchemy."""

from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.config import settings

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url_async)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = None


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Run migrations with connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = settings.database_url_async
    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio

    asyncio.run(run_migrations_online())

