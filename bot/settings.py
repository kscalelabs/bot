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
class UserSettings:
    admin_emails: list[str] = ml.conf_field(MISSING)
    # The field below is used to restrict the development server to only
    # authorized users, to prevent random people from creating accounts.
    authorized_users: list[str] | None = ml.conf_field(None)


@dataclass
class SiteSettings:
    homepage: str = ml.conf_field(MISSING)


@dataclass
class SQLiteDatabaseSettings:
    host: str = ml.conf_field(MISSING)


@dataclass
class PostgreSQLEndpointSettings:
    host: str = ml.conf_field(MISSING)
    port: int = ml.conf_field(MISSING)
    username: str = ml.conf_field(MISSING)
    password: str = ml.conf_field(MISSING)
    database: str = ml.conf_field("postgres")


@dataclass
class PostgreSQLDatabaseSettings:
    write_endpoint: PostgreSQLEndpointSettings = ml.conf_field(PostgreSQLEndpointSettings())
    read_endpoint: PostgreSQLEndpointSettings = ml.conf_field(II("database.postgres.write_endpoint"))


@dataclass
class DatabaseSettings:
    kind: str = ml.conf_field(MISSING)
    sqlite: SQLiteDatabaseSettings = ml.conf_field(SQLiteDatabaseSettings())
    postgres: PostgreSQLDatabaseSettings = ml.conf_field(PostgreSQLDatabaseSettings())


@dataclass
class RabbitMessageQueueSettings:
    host: str = ml.conf_field("localhost")
    port: int = ml.conf_field(5672)
    virtual_host: str = ml.conf_field("/")
    username: str = ml.conf_field("guest")
    password: str = ml.conf_field("guest")
    queue_name: str = ml.conf_field("dpsh")


@dataclass
class SqsMessageQueueSettings:
    queue_name: str = ml.conf_field(MISSING)


@dataclass
class WorkerSettings:
    model_key: str = ml.conf_field(MISSING)
    queue_type: str = ml.conf_field(MISSING)
    rabbit: RabbitMessageQueueSettings = ml.conf_field(RabbitMessageQueueSettings())
    sqs: SqsMessageQueueSettings = ml.conf_field(SqsMessageQueueSettings())
    sampling_timesteps: int | None = ml.conf_field(None)
    soft_time_limit: int = ml.conf_field(30)
    max_retries: int = ml.conf_field(3)


@dataclass
class AudioFileSettings:
    file_ext: str = ml.conf_field("flac")
    sample_rate: int = ml.conf_field(16000)
    min_sample_rate: int = ml.conf_field(8000)
    sample_width: int = ml.conf_field(2)
    num_channels: int = ml.conf_field(1)
    res_type: str = ml.conf_field("kaiser_fast")
    max_mb: int = ml.conf_field(10)
    max_duration: float = ml.conf_field(10.0)


@dataclass
class S3FileSettings:
    bucket: str = ml.conf_field(MISSING)
    url_expiration: int = ml.conf_field(3600)


@dataclass
class FileSettings:
    fs_type: str = ml.conf_field(MISSING)
    root_dir: str = ml.conf_field(MISSING)
    audio: AudioFileSettings = ml.conf_field(AudioFileSettings())
    s3: S3FileSettings = ml.conf_field(S3FileSettings())


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
    user: UserSettings = ml.conf_field(UserSettings())
    site: SiteSettings = ml.conf_field(SiteSettings())
    database: DatabaseSettings = ml.conf_field(DatabaseSettings())
    worker: WorkerSettings = ml.conf_field(WorkerSettings())
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
