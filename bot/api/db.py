"""Defines the utility functions for interacting with the database."""

import asyncio
import logging
from pathlib import Path
from typing import Any

from ml.utils.logging import configure_logging
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

    write_host, read_host = settings.database.postgres.write_host, settings.database.postgres.read_host

    def get_connections() -> dict:
        if write_host == read_host:
            return {
                "default": {
                    "engine": "tortoise.backends.asyncpg",
                    "credentials": get_credential(settings.database.postgres.write_host),
                },
            }

        return {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres.write_host),
            },
            "read_replica": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": get_credential(settings.database.postgres.read_host),
            },
        }

    return {
        "connections": get_connections(),
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
    logger.info("Initializing database")
    await Tortoise.init(config=get_config())
    if generate_schemas:
        await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.info("Closing database")
    await Tortoise.close_connections()


class _LazyLoadConfig:
    def __init__(self) -> None:
        super().__init__()

        self._config: dict | None = None

    def __getattribute__(self, name: str) -> Any:  # noqa: ANN401
        if name == "_config":
            config = super().__getattribute__(name)
            if config is None:
                config = get_config()
                super().__setattr__(name, config)
            return config
        return self._config.__getattribute__(name)

    def __getitem__(self, key: str) -> Any:  # noqa: ANN401
        assert (config := self._config) is not None
        return config.__getitem__(key)


CONFIG = _LazyLoadConfig()


async def main() -> None:
    configure_logging()
    await init_db(generate_schemas=True)
    await close_db()


if __name__ == "__main__":
    # python -m bot.api.db
    asyncio.run(main())
