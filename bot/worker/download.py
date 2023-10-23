"""Ensures that the pretrained model weights are downloaded."""

import logging

from ml.utils.logging import configure_logging

from bot.model.hubert.pretrained import pretrained_hubert
from bot.worker.model import MODEL

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    pretrained_hubert(MODEL)
    logger.info("Done.")


if __name__ == "__main__":
    # python -m bot.worker.download
    main()
