"""Defines the model runner worker code."""

import asyncio
import logging
import time

from bot.worker.message_passing import get_message_queue, Message
import ml.api as ml
import torch
from bot.utils import server_time, configure_logging

from bot.api.audio import load_audio_array, save_audio_array
from bot.api.db import close_db, init_db
from bot.api.model import Generation
from bot.model.hubert.model import HubertModel
from bot.settings import load_settings

from bot.model.hubert.checkpoint import cast_pretrained_model, pretrained_hubert
from bot.model.hubert.model import HubertModel
from bot.settings import load_settings

logger = logging.getLogger(__name__)

settings = load_settings().worker


class _ModelRunner:
    def __init__(self) -> None:
        super().__init__()

        self._model: HubertModel | None = None
        self._device: ml.base_device | None = None
        self._model_key: str | None = None

    def initialize(self) -> None:
        device = ml.detect_device()
        settings = load_settings().worker
        model = pretrained_hubert(cast_pretrained_model(settings.model_key))
        model.eval()
        device.module_to(model)
        self._model = model
        self._device = device
        self._model_key = settings.model_key

    @property
    def model(self) -> HubertModel:
        assert self._model is not None, "Model not initialized."
        return self._model

    @property
    def device(self) -> ml.base_device:
        assert self._device is not None, "Model not initialized."
        return self._device

    @property
    def model_key(self) -> str:
        assert self._model_key is not None, "Model not initialized."
        return self._model_key

model_runner = _ModelRunner()


async def run_model(message: Message) -> None:
    generation = await Generation.get_or_none(uuid=message.generation_uuid).prefetch_related("output")
    if generation is None:
        raise ValueError("Generation not found.")

    # Gets the input UUIDs.
    source_uuid, reference_uuid = generation.source_id, generation.reference_id

    start_time = time.time()

    # Gets properties from the model runner.
    device = model_runner.device
    model = model_runner.model
    model_key = model_runner.model_key

    source_audio_arr, reference_audio_arr = await asyncio.gather(
        load_audio_array(source_uuid),
        load_audio_array(reference_uuid),
    )

    source_audio, reference_audio = device.tensor_to(source_audio_arr), device.tensor_to(reference_audio_arr)
    source_audio, reference_audio = source_audio.unsqueeze(0), reference_audio.unsqueeze(0)

    # Runs the model.
    with device.autocast_context(), torch.inference_mode():
        output_audio = model.run(source_audio, reference_audio, settings.sampling_timesteps)

    # Updates the generation information.
    elapsed_time = time.time() - start_time
    generation.elapsed_time = elapsed_time
    generation.model = model_key
    generation.task_finished = server_time()

    # Saves the output audio.
    output_audio_arr = output_audio.squeeze(0).float().cpu().numpy()
    await asyncio.gather(save_audio_array(generation.output, output_audio_arr), generation.save())


async def worker_fn() -> None:
    configure_logging()

    await init_db()

    try:
        mq = get_message_queue()
        mq.initialize()
        await mq.receive(run_model)

    finally:
        logger.info("Cleaning up...")
        await close_db()
