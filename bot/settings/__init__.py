"""Defines the bot settings."""

import functools
import os
from pathlib import Path
from typing import Any, cast

from omegaconf import OmegaConf

from bot.settings.structure import Settings


@functools.lru_cache()
def _load(key: str | None = None) -> Settings:
    """Loads the bot settings.

    This function first looks for the config at ``$DPSH_CONFIG``, and if not,
    defaults to using whatever config is at ``~/.config/dpsh.yaml``.

    Args:
        key: A key referencing specific settings.

    Returns:
        The bot settings dataclass.
    """
    if key is None:
        key = os.environ["DPSH_CONFIG_KEY"]

    def _check_exists(path: Path) -> Path:
        if not path.exists():
            raise ValueError(f"Directory not found: {path}")
        return path

    base_dir = (Path(__file__).parent / "configs").resolve()
    conf_dir = _check_exists(base_dir / key)
    raw_configs = (OmegaConf.load(config) for config in conf_dir.glob("*.yaml"))
    config = OmegaConf.merge(OmegaConf.structured(Settings), *raw_configs)
    OmegaConf.resolve(config)
    return cast(Settings, config)


# The settings are loaded here so that they are only loaded once.
settings = _load()
