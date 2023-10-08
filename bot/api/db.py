"""Defines the utility functions for interacting with the database."""

from tortoise import Tortoise

from bot.settings import load_settings


async def init_db() -> None:
    settings = await load_settings()
    host = settings.database.host
    port = settings.database.port
    path = settings.database.path
    username = settings.database.username
    password = settings.database.password

    await Tortoise.init(
        db_url=f"postgres://{username}:{password}@{host}:{port}{path}",
        modules={"models": ["models"]},
    )
    await Tortoise.generate_schemas()
