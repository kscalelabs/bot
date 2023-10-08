"""Voice changer backend code."""

import argparse
import logging

import ml.api as ml
import numpy as np
import sounddevice as sd
import torch
from codec.pretrained.hubert import pretrained_hubert

logger = logging.getLogger(__name__)


class VoiceChanger:
    def __init__(self) -> None:
        super().__init__()

        self.model = pretrained_hubert("no-quantization")
        self.device = ml.detect_device()
        self.device.module_to(self.model)
        self.sampling_rate = 16000

    @torch.no_grad()
    def change_voice(self, audio: np.ndarray, speaker_id: int) -> np.ndarray:
        speaker_id_tensor = torch.tensor([speaker_id], dtype=torch.long, device=self.device._get_device())
        audio_tensor = self.device.tensor_to(audio)
        with self.device.autocast_context():
            converted_audio = self.model.run(audio_tensor, speaker_id_tensor, sampling_timesteps=50)
        return ml.as_numpy_array(converted_audio)


def run_adhoc() -> None:
    ml.configure_logging()

    parser = argparse.ArgumentParser(description="Runs the voice changer offline.")
    parser.add_argument("-s", "--num-seconds", type=int, default=10)
    args = parser.parse_args()

    voice_changer = VoiceChanger()
    sr = voice_changer.sampling_rate
    num_seconds: int = args.num_seconds

    for speaker_id in range(250):
        logger.info("Recording %d seconds of audio...", num_seconds)
        audio = sd.rec(int(num_seconds * sr), samplerate=sr, channels=1, dtype="float32")
        sd.wait()
        logger.info("Done recording.")

        logger.info("Changing voice...")
        converted_audio = voice_changer.change_voice(audio.transpose(1, 0), speaker_id)
        logger.info("Done changing voice.")

        logger.info("Playing back audio...")
        sd.play(converted_audio.transpose(1, 0), sr)
        sd.wait()
        logger.info("Done playing back audio.")


if __name__ == "__main__":
    # python -m bot.voice_changer
    run_adhoc()
