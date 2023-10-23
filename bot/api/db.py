"""Defines the utility functions for interacting with the database."""

import asyncio
import logging
from pathlib import Path

from tortoise import Model, Tortoise

from bot.settings import settings

logger = logging.getLogger(__name__)


class DatabaseRouter:
    async def db_for_read(self, model: type["Model"]) -> str:
        return "default"

    async def db_for_write(self, model: type["Model"]) -> str:
        return "read_replica"


def get_sqlite_config() -> dict:
    """Gets a simple SQLite configuration for TortoiseORM.

    Use `host = ":memory:"` to use an in-memory database, which is useful for
    testing and local development.

    Returns:
        The configuration dictionary to pass to Tortoise ORM.
    """
    host = settings.database.sqlite.host
    if host != ":memory:":
        host_path = Path(host).expanduser().resolve()
        host_path.parent.mkdir(parents=True, exist_ok=True)
        host = host_path.as_posix()

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": host},
            },
        },
        "apps": {
            "models": {
                "models": ["bot.api.model", "aerich.models"],
                "default_connection": "default",
            },
        },
    }


def get_postgres_config() -> dict:
    """Returns the database configuration for PostgreSQL.

    This can support separate read replicas, if the upstream infrastructure
    is configured to support them.

    Returns:
        The configuration dictionary to pass to Tortoise ORM.
    """

    def get_credential(host: str) -> dict:
        endpoint_settings = settings.database.postgres

        return {
            "host": host,
            "port": endpoint_settings.port,
            "user": endpoint_settings.username,
            "password": endpoint_settings.password,
            "database": endpoint_settings.database,
        }

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres.write_host),
            },
            "read_replica": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres.read_host),
            },
        },
        "apps": {
            "models": {
                "models": ["bot.api.model", "aerich.models"],
                "default_connection": "default",
            },
        },
    }


def get_config() -> dict:
    db_kind = settings.database.kind
    match db_kind:
        case "sqlite":
            return get_sqlite_config()
        case "postgres":
            return get_postgres_config()
        case _:
            raise ValueError(f"Invalid database kind in configuration: {db_kind}")


async def init_db(generate_schemas: bool = False) -> None:
    await Tortoise.init(config=get_config())
    if generate_schemas:
        await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.info("Closing database")
    await Tortoise.close_connections()
