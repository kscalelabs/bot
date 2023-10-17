"""Defines the bot settings."""

import functools
import os
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from ml.core.config import conf_field
from omegaconf import II, MISSING, OmegaConf


@dataclass
class UserSettings:
    admin_emails: list[str] = conf_field(MISSING)
    # The field below is used to restrict the development server to only
    # authorized users, to prevent random people from creating accounts.
    authorized_users: list[str] | None = conf_field(None)


@dataclass
class SiteSettings:
    homepage: str = conf_field(MISSING)


@dataclass
class SQLiteDatabaseSettings:
    host: str = conf_field(MISSING)


@dataclass
class PostgreSQLEndpointSettings:
    host: str = conf_field(MISSING)
    port: int = conf_field(MISSING)
    username: str = conf_field(MISSING)
    password: str = conf_field(MISSING)
    database: str = conf_field("postgres")


@dataclass
class PostgreSQLDatabaseSettings:
    write_endpoint: PostgreSQLEndpointSettings = conf_field(PostgreSQLEndpointSettings())
    read_endpoint: PostgreSQLEndpointSettings = conf_field(II("database.postgres.write_endpoint"))


@dataclass
class DatabaseSettings:
    kind: str = conf_field(MISSING)
    sqlite: SQLiteDatabaseSettings = conf_field(SQLiteDatabaseSettings())
    postgres: PostgreSQLDatabaseSettings = conf_field(PostgreSQLDatabaseSettings())


@dataclass
class RabbitMessageQueueSettings:
    host: str = conf_field("localhost")
    port: int = conf_field(5672)
    virtual_host: str = conf_field("/")
    username: str = conf_field("guest")
    password: str = conf_field("guest")
    queue_name: str = conf_field("dpsh")


@dataclass
class SqsMessageQueueSettings:
    queue_name: str = conf_field(MISSING)


@dataclass
class WorkerSettings:
    model_key: str = conf_field(MISSING)
    queue_type: str = conf_field(MISSING)
    rabbit: RabbitMessageQueueSettings = conf_field(RabbitMessageQueueSettings())
    sqs: SqsMessageQueueSettings = conf_field(SqsMessageQueueSettings())
    sampling_timesteps: int | None = conf_field(None)
    soft_time_limit: int = conf_field(30)
    max_retries: int = conf_field(3)


@dataclass
class AudioFileSettings:
    file_ext: str = conf_field("flac")
    sample_rate: int = conf_field(16000)
    min_sample_rate: int = conf_field(8000)
    sample_width: int = conf_field(2)
    num_channels: int = conf_field(1)
    res_type: str = conf_field("kaiser_fast")
    max_mb: int = conf_field(10)
    max_duration: float = conf_field(10.0)


@dataclass
class S3FileSettings:
    bucket: str = conf_field(MISSING)
    url_expiration: int = conf_field(3600)


@dataclass
class FileSettings:
    fs_type: str = conf_field(MISSING)
    root_dir: str = conf_field(MISSING)
    audio: AudioFileSettings = conf_field(AudioFileSettings())
    s3: S3FileSettings = conf_field(S3FileSettings())


@dataclass
class EmailSettings:
    host: str = conf_field(MISSING)
    port: int = conf_field(MISSING)
    name: str = conf_field(MISSING)
    email: str = conf_field(MISSING)
    password: str = conf_field(MISSING)


@dataclass
class CryptoSettings:
    jwt_secret: str = conf_field(MISSING)
    expire_token_minutes: int = conf_field(30)
    expire_otp_minutes: int = conf_field(5)
    algorithm: str = conf_field("HS256")
    google_client_id: str = conf_field(MISSING)


@dataclass
class ModelSettings:
    hf_hub_token: str | None = conf_field(None)
    cache_dir: str | None = conf_field(None)


@dataclass
class Settings:
    app_name: str = conf_field("bot")
    is_prod: bool = conf_field(True)
    user: UserSettings = conf_field(UserSettings())
    site: SiteSettings = conf_field(SiteSettings())
    database: DatabaseSettings = conf_field(DatabaseSettings())
    worker: WorkerSettings = conf_field(WorkerSettings())
    file: FileSettings = conf_field(FileSettings())
    email: EmailSettings = conf_field(EmailSettings())
    crypto: CryptoSettings = conf_field(CryptoSettings())
    model: ModelSettings = conf_field(ModelSettings())


@functools.lru_cache()
def load_settings() -> Settings:
    """Loads the bot settings.

    This function first looks for the config at ``$DPSH_CONFIG``, and if not,
    defaults to using whatever config is at ``~/.config/dpsh.yaml``.

    Returns:
        The bot settings dataclass.
    """
    config = OmegaConf.structured(Settings)
    raw_config_path = Path(os.environ.get("DPSH_CONFIG", "~/.config/dpsh.yaml")).expanduser().resolve()
    if raw_config_path.exists():
        raw_config = OmegaConf.load(raw_config_path)
        config = OmegaConf.merge(config, raw_config)
    OmegaConf.resolve(config)
    return cast(Settings, config)
