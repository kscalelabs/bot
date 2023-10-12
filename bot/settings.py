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
class FileSettings:
    fs_type: str = ml.conf_field(MISSING)
    root_dir: str = ml.conf_field(MISSING)
    audio_file_ext: str = ml.conf_field("flac")
    audio_sample_rate: int = ml.conf_field(16000)
    audio_min_sample_rate: int = ml.conf_field(8000)
    audio_res_type: str = ml.conf_field("kaiser_fast")
    audio_max_mb: int = ml.conf_field(10)
    audio_max_duration: float = ml.conf_field(10.0)
    s3_bucket: str = ml.conf_field(MISSING)


@dataclass
class EmailSettings:
    host: str = ml.conf_field(MISSING)
    port: int = ml.conf_field(MISSING)
    name: str = ml.conf_field(MISSING)
    email: str = ml.conf_field(MISSING)
    password: str = ml.conf_field(MISSING)


@dataclass
class CryptoSettings:
    jwt_secret: str = ml.conf_field(MISSING)
    expire_token_minutes: int = ml.conf_field(30)
    expire_otp_minutes: int = ml.conf_field(5)
    algorithm: str = ml.conf_field("HS256")
    google_client_id: str = ml.conf_field(MISSING)


@dataclass
class Settings:
    app_name: str = ml.conf_field("bot")
    version: str = ml.conf_field(II("bot.version:"))
    is_prod: bool = ml.conf_field(True)
    site: SiteSettings = ml.conf_field(SiteSettings())
    database: DatabaseSettings = ml.conf_field(DatabaseSettings())
    file: FileSettings = ml.conf_field(FileSettings())
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
    if "DPSH_BOT_CONFIG" in os.environ:
        raw_config = OmegaConf.create(os.environ["DPSH_BOT_CONFIG"])
        config = OmegaConf.merge(OmegaConf.structured(Settings), raw_config)
    else:
        root = Path.home() / ".config" / "dpsh-bot"
        config_paths = root.glob("*.yaml")
        raw_configs = (OmegaConf.load(config) for config in config_paths)
        config = OmegaConf.merge(OmegaConf.structured(Settings), *raw_configs)
    OmegaConf.resolve(config)
    return cast(Settings, config)
