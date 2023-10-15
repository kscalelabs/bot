"""Defines Bot-wide utility functions."""

import datetime
import logging
import math
import sys

from typing import Literal

RESET_SEQ = "\033[0m"
REG_COLOR_SEQ = "\033[%dm"
BOLD_COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"


Color = Literal[
    "black",
    "red",
    "green",
    "yellow",
    "blue",
    "magenta",
    "cyan",
    "white",
    "grey",
    "light-red",
    "light-green",
    "light-yellow",
    "light-blue",
    "light-magenta",
    "light-cyan",
]

COLOR_INDEX: dict[Color, int] = {
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "grey": 90,
    "light-red": 91,
    "light-green": 92,
    "light-yellow": 93,
    "light-blue": 94,
    "light-magenta": 95,
    "light-cyan": 96,
}


def server_time() -> datetime.datetime:
    return datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc)


def get_colorize_parts(color: Color, bold: bool = False) -> tuple[str, str]:
    if bold:
        return BOLD_COLOR_SEQ % COLOR_INDEX[color], RESET_SEQ
    return REG_COLOR_SEQ % COLOR_INDEX[color], RESET_SEQ


def colorize(s: str, color: Color, bold: bool = False) -> str:
    start, end = get_colorize_parts(color, bold=bold)
    return start + s + end

# Logging level to show on all ranks.
INFOALL: int = logging.INFO + 1
DEBUGALL: int = logging.DEBUG + 1


class RankFilter(logging.Filter):
    def __init__(self, *, rank: int | None = None) -> None:
        """Logging filter which filters out INFO logs on non-zero ranks.

        Args:
            rank: The current rank
        """
        super().__init__()

        self.rank = rank

        # Log using INFOALL to show on all ranks.
        logging.addLevelName(INFOALL, "INFOALL")
        logging.addLevelName(DEBUGALL, "DEBUGALL")
        levels_to_log_all_ranks = (DEBUGALL, INFOALL, logging.CRITICAL, logging.ERROR, logging.WARNING)
        self.log_all_ranks = {logging.getLevelName(level) for level in levels_to_log_all_ranks}

    def filter(self, record: logging.LogRecord) -> bool:
        if self.rank is None or self.rank == 0:
            return True
        if record.levelname in self.log_all_ranks:
            return True
        return False


class ColoredFormatter(logging.Formatter):
    """Defines a custom formatter for displaying logs."""

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[1;%dm"
    BOLD_SEQ = "\033[1m"

    COLORS: dict[str, Color] = {
        "WARNING": "yellow",
        "INFOALL": "magenta",
        "INFO": "cyan",
        "DEBUGALL": "grey",
        "DEBUG": "grey",
        "CRITICAL": "yellow",
        "FATAL": "red",
        "ERROR": "red",
    }

    def __init__(
        self,
        *,
        prefix: str | None = None,
        rank: int | None = None,
        world_size: int | None = None,
        use_color: bool = True,
    ) -> None:
        asc_start, asc_end = get_colorize_parts("grey")
        message = "{levelname:^19s} " + asc_start + "{asctime}" + asc_end + " [{name}] {message}"
        if prefix is not None:
            message = colorize(prefix, "white") + " " + message
        if rank is not None or world_size is not None:
            assert rank is not None and world_size is not None
            digits = int(math.log10(world_size) + 1)
            message = "[" + colorize(f"{rank:>{digits}}", "blue", bold=True) + "] " + message
        super().__init__(message, style="{", datefmt="%Y-%m-%d %H:%M:%S")

        self.rank = rank
        self.use_color = use_color

    def format(self, record: logging.LogRecord) -> str:
        levelname = record.levelname

        match levelname:
            case "DEBUG":
                record.levelname = ""
            case "INFOALL":
                record.levelname = "INFO"
            case "DEBUGALL":
                record.levelname = "DEBUG"

        if record.levelname and self.use_color and levelname in self.COLORS:
            record.levelname = colorize(record.levelname, self.COLORS[levelname], bold=True)
        return logging.Formatter.format(self, record)


def configure_logging(
    *,
    prefix: str | None = None,
    rank: int | None = None,
    world_size: int | None = None,
    use_tqdm: bool = True,
) -> None:
    """Instantiates print logging, to either stdout or tqdm.

    Args:
        prefix: An optional prefix to add to the logger
        rank: The current rank, or None if not using multiprocessing
        world_size: The total world size, or None if not using multiprocessing
        use_tqdm: Write using TQDM instead of sys.stdout
    """
    if rank is not None or world_size is not None:
        assert rank is not None and world_size is not None
    root_logger = logging.getLogger()
    while root_logger.hasHandlers():
        root_logger.removeHandler(root_logger.handlers[0])

    try:
        import tqdm  # noqa: F401
    except ImportError:
        use_tqdm = False

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(ColoredFormatter(prefix=prefix, rank=rank, world_size=world_size))
    handler.addFilter(RankFilter(rank=rank))
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
