"""Defines the utility functions for interacting with the database."""

import logging

from tortoise import Tortoise

from bot.settings import load_settings

logger = logging.getLogger(__name__)


async def init_db_sqlite() -> None:
    settings = load_settings().database.sqlite
    logger.info("Initializing SQLite database")
    await Tortoise.init(db_url=f"sqlite://{settings.host}", modules={"models": ["bot.api.model"]})


async def init_db_postgres() -> None:
    settings = load_settings().database.postgres

    logger.info("Initializing PostgreSQL database")
    await Tortoise.init(
        config={
            "connections": {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": {
                        "host": settings.host,
                        "port": settings.port,
                        "user": settings.username,
                        "password": settings.password,
                        "database": settings.database,
                    },
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
