"""Defines the model runner worker code."""

import asyncio
import logging
import os
import time
from typing import cast, get_args

import torch
from ml.utils.device.auto import detect_device
from torch import Tensor
from tortoise.transactions import in_transaction

from bot.api.audio import load_audio_array, save_audio_array
from bot.api.model import Audio, AudioSource, Generation, Task
from bot.model.hubert.pretrained import PretrainedHubertModel, pretrained_hubert
from bot.settings import settings

logger = logging.getLogger(__name__)


def get_model() -> PretrainedHubertModel:
    key = os.environ.get("DPSH_MODEL", "hubert-quantized-20231015")
    if key not in get_args(PretrainedHubertModel):
        raise ValueError(f"Invalid pretrained HuBERT model: {key}")
    return cast(PretrainedHubertModel, key)


MODEL: PretrainedHubertModel = get_model()


class ModelRunner:
    def __init__(self, num_timesteps: int | None = None) -> None:
        super().__init__()

        self.num_timesteps = settings.worker.sampling_timesteps if num_timesteps is None else num_timesteps

        device = detect_device()
        model = pretrained_hubert(MODEL)
        model.eval()
        device.module_to(model)

        self.device = device
        self.model = model
        self.model_key = MODEL

    async def load_samples(self, src: Audio, ref: Audio) -> tuple[Tensor, Tensor]:
        src_audio_arr, ref_audio_arr = await asyncio.gather(
            load_audio_array(src.key),
            load_audio_array(ref.key),
        )
        src_audio_arr = src_audio_arr.astype("float32") / 32768
        ref_audio_arr = ref_audio_arr.astype("float32") / 32768
        return torch.from_numpy(src_audio_arr), torch.from_numpy(ref_audio_arr)

    async def run_model(self, src_audio: Tensor, ref_audio: Tensor) -> tuple[Tensor, float]:
        start_time = time.time()
        src_audio = self.device.tensor_to(src_audio).unsqueeze(0)
        ref_audio = self.device.tensor_to(ref_audio).unsqueeze(0)
        with self.device.autocast_context(), torch.inference_mode():
            output_audio = self.model.run(src_audio, ref_audio, self.num_timesteps)
        output_audio.squeeze(0).float().cpu()
        return output_audio, time.time() - start_time

    async def process_output(
        self,
        src: Audio,
        ref: Audio,
        output_audio: Tensor,
        elapsed_time: float,
    ) -> tuple[Audio, Generation]:
        output_audio_arr = output_audio.squeeze(0).float().cpu().numpy()
        output_audio_arr = (output_audio_arr * 32768).clip(-32768, 32767).astype("int16")
        async with in_transaction():
            output = await save_audio_array(
                user_id=src.user_id,
                source=AudioSource.generated,
                audio_array=output_audio_arr,
                name=f"{src.name} to {ref.name}",
            )
            generation = await Generation.create(
                user_id=output.user_id,
                source=src,
                reference=ref,
                output=output,
                model=self.model_key,
                elapsed_time=elapsed_time,
            )
            await Task.create(
                user_id=output.user_id,
                source=src,
                reference=ref,
                output=output,
                model=self.model_key,
                elapsed_time=elapsed_time,
            )
        return output, generation
