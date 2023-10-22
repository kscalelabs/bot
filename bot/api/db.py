"""Defines the utility functions for interacting with the database."""

import logging

from tortoise import Model, Tortoise

from bot.settings import env_settings as settings
from bot.settings.environment import PostgreSQLDatabaseSettings

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
    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": settings.database.sqlite.host},
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

    def get_credential(endpoint_settings: "PostgreSQLDatabaseSettings") -> dict:
        return {
            "host": endpoint_settings.host,
            "port": endpoint_settings.port,
            "user": endpoint_settings.username,
            "password": endpoint_settings.password,
            "database": endpoint_settings.database,
        }

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres),
            },
            "read_replica": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres),
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
