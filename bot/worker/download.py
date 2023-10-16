"""Ensures that the pretrained model weights are downloaded."""

from bot.model.hubert.pretrained import cast_pretrained_model, pretrained_hubert
from bot.settings import load_settings


def main() -> None:
    settings = load_settings().worker
    pretrained_hubert(cast_pretrained_model(settings.model_key))
    print("Done.")


if __name__ == "__main__":
    # python -m bot.worker.download
    main()
