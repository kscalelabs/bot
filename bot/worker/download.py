"""Ensures that the pretrained model weights are downloaded."""

import logging

from ml.utils.logging import configure_logging

from bot.model.hubert.pretrained import cast_pretrained_model, pretrained_hubert
from bot.settings import settings

logger = logging.getLogger(__name__)


def main() -> None:
    configure_logging()
    pretrained_hubert(cast_pretrained_model(settings.worker.model_key))
    logger.info("Done.")


if __name__ == "__main__":
    # python -m bot.worker.download
    main()
