"""Defines the bot settings."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import ml.api as ml
from omegaconf import MISSING, OmegaConf

from bot import __version__ as bot_version


@dataclass
class DatabaseSettings:
    url: str = ml.conf_field(MISSING)
    port: int = ml.conf_field(MISSING)
    username: str = ml.conf_field(MISSING)
    password: str = ml.conf_field(MISSING)


@dataclass
class Settings:
    app_name: str = ml.conf_field("bot")
    version: str = ml.conf_field(MISSING)
    database: DatabaseSettings = ml.conf_field(DatabaseSettings())


def load() -> Settings:
    """Loads the bot settings.

    This function looks in ``~/.config/dpsh-bot/*.yaml`` and
    ``$DPSH_BOT_CONFIG_ROOT/*.yaml`` for configuration files. The configuration
    files are merged together, with the latter taking precedence.

    Returns:
        The bot settings dataclass.
    """
    config_paths = [*(Path.home() / ".config" / "dpsh-bot").glob("*.yaml")]
    if "DPSH_BOT_CONFIG_ROOT" in os.environ:
        config_paths.extend(Path(os.environ["DPSH_BOT_CONFIG_ROOT"]).glob("*.yaml"))
    raw_configs = OmegaConf.load(config_paths)
    config = cast(Settings, OmegaConf.merge(OmegaConf.structured(Settings), *raw_configs))
    config.version = bot_version
    return config
