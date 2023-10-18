"""Defines the utility functions for interacting with the database."""

import logging

from tortoise import Model, Tortoise

from bot.settings import PostgreSQLEndpointSettings, load_settings

logger = logging.getLogger(__name__)


class DatabaseRouter:
    async def db_for_read(self, model: type["Model"]) -> str:
        return "default"

    async def db_for_write(self, model: type["Model"]) -> str:
        return "read_replica"


def get_sqlite_config() -> dict:
    settings = load_settings().database.sqlite

    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.sqlite",
                "credentials": {"file_path": settings.host},
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
    settings = load_settings().database.postgres

    def get_credential(endpoint_settings: "PostgreSQLEndpointSettings") -> dict:
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
                "credentials": get_credential(settings.write_endpoint),
            },
            "read_replica": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.read_endpoint),
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
    db_kind = load_settings().database.kind

    match db_kind:
        case "sqlite":
            return get_sqlite_config()
        case "postgres":
            return get_postgres_config()
        case _:
            raise ValueError(f"Invalid database kind in configuration: {db_kind}")


async def init_db() -> None:
    await Tortoise.init(config=get_config())
    # await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.info("Closing database")
    await Tortoise.close_connections()
