"""Defines the bot settings."""

import os
from pathlib import Path
from typing import Any, Callable, Generic, TypeVar, cast

from omegaconf import DictConfig, OmegaConf

from bot.settings.environment import EnvironmentSettings

T = TypeVar("T")


def _check_exists(path: Path) -> Path:
    if not path.exists():
        raise ValueError(f"Directory not found: {path}")
    return path


def _load_environment_settings() -> EnvironmentSettings:
    environment = os.environ["DPSH_ENVIRONMENT"]
    base_dir = (Path(__file__).parent / "configs").resolve()
    config_path = _check_exists(base_dir / f"{environment}.yaml")
    config = OmegaConf.load(config_path)
    config = OmegaConf.merge(OmegaConf.structured(EnvironmentSettings), config)
    OmegaConf.resolve(config)
    settings = cast(EnvironmentSettings, config)
    settings.environment = environment
    return settings


class _LazyLoadSettings(Generic[T]):
    def __init__(self, func: Callable[[], T]) -> None:
        super().__init__()

        self._lazy_load_func = func
        self._lazy_load_value: T | None = None

    def __getattribute__(self, name: str) -> Any:  # noqa: ANN401
        if name in ("_lazy_load_func", "_lazy_load_value"):
            return super().__getattribute__(name)
        value = super().__getattribute__("_lazy_load_value")
        if value is None:
            func = super().__getattribute__("_lazy_load_func")
            value = func()
            super().__setattr__("_lazy_load_value", value)
        return getattr(value, name)


settings = cast(EnvironmentSettings, _LazyLoadSettings(_load_environment_settings))
