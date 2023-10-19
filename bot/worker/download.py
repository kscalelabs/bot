"""Ensures that the pretrained model weights are downloaded."""

from bot.model.hubert.pretrained import cast_pretrained_model, pretrained_hubert
from bot.settings import settings


def main() -> None:
    pretrained_hubert(cast_pretrained_model(settings.worker.model_key))
    print("Done.")


if __name__ == "__main__":
    # python -m bot.worker.download
    main()
