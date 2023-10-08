"""Defines the bot settings."""

import functools
import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import ml.api as ml
from omegaconf import II, MISSING, OmegaConf

from bot import __version__ as bot_version

# Register the bot version as a resolver so that it can be referenced
# in the configuration files.
OmegaConf.register_new_resolver("bot.version", lambda: bot_version, use_cache=True)


@dataclass
class SiteSettings:
    homepage: str = ml.conf_field(MISSING)


@dataclass
class DatabaseSettings:
    kind: str = ml.conf_field(MISSING)
    host: str = ml.conf_field(MISSING)
    port: int | None = ml.conf_field(MISSING)
    path: str | None = ml.conf_field(MISSING)
    username: str | None = ml.conf_field(MISSING)
    password: str | None = ml.conf_field(MISSING)


@dataclass
class ImageSettings:
    # When reading and writing images to S3, use `safe_open` to ensure that
    # the file is closed after reading/writing.
    root_dir: str = ml.conf_field(MISSING)


@dataclass
class EmailSettings:
    host: str = ml.conf_field(MISSING)
    port: int = ml.conf_field(MISSING)
    name: str = ml.conf_field(MISSING)
    email: str = ml.conf_field(MISSING)
    password: str = ml.conf_field(MISSING)


@dataclass
class CryptoSettings:
    jwt_secret: str = ml.conf_field(II("oc.env:BOT_JWT_SECRET"))


@dataclass
class Settings:
    app_name: str = ml.conf_field("bot")
    version: str = ml.conf_field(II("bot.version:"))
    site: SiteSettings = ml.conf_field(SiteSettings())
    database: DatabaseSettings = ml.conf_field(DatabaseSettings())
    image: ImageSettings = ml.conf_field(ImageSettings())
    email: EmailSettings = ml.conf_field(EmailSettings())
    crypto: CryptoSettings = ml.conf_field(CryptoSettings())


@functools.lru_cache()
def load_settings() -> Settings:
    """Loads the bot settings.

    This function looks in ``~/.config/dpsh-bot/*.yaml`` and
    ``$DPSH_BOT_CONFIG_ROOT/*.yaml`` for configuration files. The configuration
    files are merged together, with the latter taking precedence.

    Returns:
        The bot settings dataclass.
    """
    root = Path.home() / ".config" / "dpsh-bot"
    config_paths = root.glob("*.yaml")
    if "DPSH_BOT_CONFIG_ROOT" in os.environ:
        config_paths.extend(Path(os.environ["DPSH_BOT_CONFIG_ROOT"]).glob("*.yaml"))
    raw_configs = (OmegaConf.load(config) for config in config_paths)
    config = cast(Settings, OmegaConf.merge(OmegaConf.structured(Settings), *raw_configs))
    config.version = bot_version
    return config
