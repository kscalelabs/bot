"""Defines the model runner worker code."""

import asyncio
import logging
import time

import ml.api as ml
import torch

from bot.api.audio import load_audio_array, save_audio_array
from bot.api.db import close_db, init_db
from bot.api.model import AudioSource, Generation
from bot.model.hubert.checkpoint import cast_pretrained_model, pretrained_hubert
from bot.model.hubert.model import HubertModel
from bot.settings import load_settings
from bot.utils import configure_logging, server_time
from bot.worker.message_passing import get_message_queue

logger = logging.getLogger(__name__)

settings = load_settings().worker


class _ModelRunner:
    def __init__(self) -> None:
        super().__init__()

        self._model: HubertModel | None = None
        self._device: ml.base_device | None = None
        self._model_key: str | None = None

    async def initialize(self) -> None:
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


async def run_model(generation_id: int) -> None:
    logger.info("Processing %s", generation_id)

    # generation = await Generation.get_or_none(id=generation_id)
    generation = await Generation.filter(id=generation_id).prefetch_related("source", "reference").get_or_none()
    if generation is None:
        raise ValueError("Generation not found.")

    try:
        source_id, reference_id, user_id = generation.source.key, generation.reference.key, generation.user_id
        name = f"{generation.source.name} to {generation.reference.name}"

        start_time = time.time()

        # Gets properties from the model runner.
        device = model_runner.device
        model = model_runner.model
        model_key = model_runner.model_key

        source_audio_arr, reference_audio_arr = await asyncio.gather(
            load_audio_array(source_id),
            load_audio_array(reference_id),
        )

        # Converts int16 to float32.
        source_audio_arr = source_audio_arr.astype("float32") / 32768
        reference_audio_arr = reference_audio_arr.astype("float32") / 32768

        source_audio, reference_audio = device.tensor_to(source_audio_arr), device.tensor_to(reference_audio_arr)
        source_audio, reference_audio = source_audio.unsqueeze(0), reference_audio.unsqueeze(0)

        # Runs the model.
        with device.autocast_context(), torch.inference_mode():
            output_audio = model.run(source_audio, reference_audio, settings.sampling_timesteps)

        # Saves the output audio.
        output_audio_arr = output_audio.squeeze(0).float().cpu().numpy()
        output_audio_arr = (output_audio_arr * 32768).clip(-32768, 32767).astype("int16")
        audio_entry = await save_audio_array(user_id, AudioSource.generated, output_audio_arr, name)

        # Updates the generation information.
        elapsed_time = time.time() - start_time
        generation.output_id = audio_entry.id
        generation.elapsed_time = elapsed_time
        generation.model = model_key
        generation.task_finished = server_time()

        await generation.save()

    except Exception:
        logger.exception("Exception while running model on %d", generation_id)
        await generation.delete()


async def worker_fn() -> None:
    configure_logging()

    # Initializes the model runner and the database.
    await asyncio.gather(model_runner.initialize(), init_db())

    try:
        mq = get_message_queue()
        await mq.initialize()
        await mq.receive(run_model)

    finally:
        logger.info("Cleaning up...")
        await close_db()