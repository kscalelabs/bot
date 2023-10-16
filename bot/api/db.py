"""Defines the utility functions for interacting with the database."""

import logging

from tortoise import Model, Tortoise

from bot.settings import PostgreSQLEndpointSettings, load_settings

logger = logging.getLogger(__name__)


async def init_db_sqlite() -> None:
    settings = load_settings().database.sqlite
    logger.info("Initializing SQLite database")
    await Tortoise.init(db_url=f"sqlite://{settings.host}", modules={"models": ["bot.api.model"]})


class DatabaseRouter:
    async def db_for_read(self, model: type["Model"]) -> str:
        return "default"

    async def db_for_write(self, model: type["Model"]) -> str:
        return "read_replica"


async def init_db_postgres() -> None:
    settings = load_settings().database.postgres

    def get_credential(endpoint_settings: "PostgreSQLEndpointSettings") -> dict:
        return {
            "host": endpoint_settings.host,
            "port": endpoint_settings.port,
            "user": endpoint_settings.username,
            "password": endpoint_settings.password,
            "database": endpoint_settings.database,
        }

    logger.info("Initializing PostgreSQL database")
    await Tortoise.init(
        config={
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
        },
    )


async def init_db() -> None:
    db_kind = load_settings().database.kind

    match db_kind:
        case "sqlite":
            await init_db_sqlite()
        case "postgres":
            await init_db_postgres()
        case _:
            raise ValueError(f"Invalid database kind in configuration: {db_kind}")

    await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.info("Closing database")
    await Tortoise.close_connections()
