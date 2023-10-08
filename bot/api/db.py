"""Defines the utility functions for interacting with the database."""

import logging

from tortoise import Tortoise

from bot.settings import load_settings

logger = logging.getLogger(__name__)


async def init_db() -> None:
    settings = load_settings()
    kind = settings.database.kind
    host = settings.database.host
    port = settings.database.port
    path = settings.database.path
    username = settings.database.username
    password = settings.database.password

    url = host
    if port is not None:
        url = f"{url}:{port}"
    if path is not None:
        url = f"{url}{path}"
    if username is not None and password is not None:
        username = f"{username}:{password}"
    if username is not None:
        url = f"{username}@{url}"
    url = f"{kind}://{host}"
    logger.info("Initializing database at %s", url)

    await Tortoise.init(
        db_url=url,
        modules={"models": ["bot.api.model"]},
    )
    await Tortoise.generate_schemas()


async def close_db() -> None:
    logger.info("Closing database")
    await Tortoise.close_connections()
