"""Defines the bot settings."""

import functools
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import cast

from omegaconf import II, MISSING, OmegaConf


@dataclass
class UserSettings:
    admin_emails: list[str] = field(default=MISSING)
    # The field below is used to restrict the development server to only
    # authorized users, to prevent random people from creating accounts.
    authorized_users: list[str] | None = field(default=None)


@dataclass
class SiteSettings:
    homepage: str = field(default=MISSING)


@dataclass
class SQLiteDatabaseSettings:
    host: str = field(default=MISSING)


@dataclass
class PostgreSQLEndpointSettings:
    host: str = field(default=MISSING)
    port: int = field(default=MISSING)
    username: str = field(default=MISSING)
    password: str = field(default=MISSING)
    database: str = field(default="postgres")


@dataclass
class PostgreSQLDatabaseSettings:
    write_endpoint: PostgreSQLEndpointSettings = field(default=PostgreSQLEndpointSettings())
    read_endpoint: PostgreSQLEndpointSettings = field(default=II("database.postgres.write_endpoint"))


@dataclass
class DatabaseSettings:
    kind: str = field(default=MISSING)
    sqlite: SQLiteDatabaseSettings = field(default=SQLiteDatabaseSettings())
    postgres: PostgreSQLDatabaseSettings = field(default=PostgreSQLDatabaseSettings())


@dataclass
class RabbitMessageQueueSettings:
    host: str = field(default="localhost")
    port: int = field(default=5672)
    virtual_host: str = field(default="/")
    username: str = field(default="guest")
    password: str = field(default="guest")
    queue_name: str = field(default="dpsh")


@dataclass
class SqsMessageQueueSettings:
    queue_name: str = field(default=MISSING)


@dataclass
class WorkerSettings:
    model_key: str = field(default=MISSING)
    queue_type: str = field(default=MISSING)
    rabbit: RabbitMessageQueueSettings = field(default=RabbitMessageQueueSettings())
    sqs: SqsMessageQueueSettings = field(default=SqsMessageQueueSettings())
    sampling_timesteps: int | None = field(default=None)
    soft_time_limit: int = field(default=30)
    max_retries: int = field(default=3)


@dataclass
class AudioFileSettings:
    file_ext: str = field(default="flac")
    sample_rate: int = field(default=16000)
    min_sample_rate: int = field(default=8000)
    sample_width: int = field(default=2)
    num_channels: int = field(default=1)
    res_type: str = field(default="kaiser_fast")
    max_mb: int = field(default=10)
    max_duration: float = field(default=10.0)


@dataclass
class S3FileSettings:
    bucket: str = field(default=MISSING)
    url_expiration: int = field(default=3600)


@dataclass
class FileSettings:
    fs_type: str = field(default=MISSING)
    root_dir: str = field(default=MISSING)
    audio: AudioFileSettings = field(default=AudioFileSettings())
    s3: S3FileSettings = field(default=S3FileSettings())


@dataclass
class EmailSettings:
    host: str = field(default=MISSING)
    port: int = field(default=MISSING)
    name: str = field(default=MISSING)
    email: str = field(default=MISSING)
    password: str = field(default=MISSING)


@dataclass
class CryptoSettings:
    jwt_secret: str = field(default=MISSING)
    expire_token_minutes: int = field(default=30)
    expire_otp_minutes: int = field(default=5)
    algorithm: str = field(default="HS256")
    google_client_id: str = field(default=MISSING)


@dataclass
class ModelSettings:
    hf_hub_token: str | None = field(default=None)
    cache_dir: str | None = field(default=None)


@dataclass
class Settings:
    app_name: str = field(default="bot")
    is_prod: bool = field(default=True)
    user: UserSettings = field(default=UserSettings())
    site: SiteSettings = field(default=SiteSettings())
    database: DatabaseSettings = field(default=DatabaseSettings())
    worker: WorkerSettings = field(default=WorkerSettings())
    file: FileSettings = field(default=FileSettings())
    email: EmailSettings = field(default=EmailSettings())
    crypto: CryptoSettings = field(default=CryptoSettings())
    model: ModelSettings = field(default=ModelSettings())


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
