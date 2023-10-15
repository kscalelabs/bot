"""Defines functions for managing audio files."""

import os
import functools
import logging
import shutil
import tempfile
import uuid
from datetime import timedelta
from typing import BinaryIO, Literal, cast, get_args
from uuid import UUID

import aioboto3
import numpy as np
from pydub import AudioSegment

from bot.api.model import Audio, AudioSource
from bot.settings import load_settings
from bot.utils import server_time

DEFAULT_NAME = "Untitled"

logger = logging.getLogger(__name__)

FSType = Literal["file", "s3"]


@functools.lru_cache()
def get_fs_type() -> FSType:
    fs_type_str = load_settings().file.fs_type
    assert fs_type_str in get_args(FSType), f"Invalid file system type in configuration: {fs_type_str}"
    return cast(FSType, fs_type_str)


def _get_path(key: UUID) -> str:
    settings = load_settings()
    return f"{settings.file.root_dir}/{key}.{settings.file.audio.file_ext}"


def _get_extension(filename: str | None, default: str) -> str:
    if filename is None:
        return default
    return filename.split(".")[-1].lower() if "." in filename else default


async def _save_audio(user_id: int, source: int, name: str | None, audio: AudioSegment) -> Audio:
    key = uuid.uuid5(uuid.NAMESPACE_OID, f"user-{user_id}-{os.urandom(16)}")
    settings = load_settings().file
    fs_type = get_fs_type()
    fs_path = _get_path(key)

    # Standardizes the audio format.
    if audio.frame_rate < settings.audio.min_sample_rate:
        raise ValueError(f"Audio sample rate must be at least {settings.audio.min_sample_rate} Hz")
    if audio.frame_rate != settings.audio.sample_rate:
        audio = audio.set_frame_rate(settings.audio.sample_rate)
    if audio.sample_width != settings.audio.sample_width:
        audio = audio.set_sample_width(settings.audio.sample_width)
    if audio.channels != settings.audio.num_channels:
        audio = audio.set_channels(settings.audio.num_channels)
    if audio.duration_seconds > settings.audio.max_duration:
        raise ValueError(f"Audio duration must be less than {settings.audio.max_duration} seconds")

    match fs_type:
        case "file":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.audio.file_ext}", delete=False) as temp_file:
                audio.export(temp_file.name, format=settings.audio.file_ext)
            shutil.move(temp_file.name, fs_path)

        case "s3":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.audio.file_ext}") as temp_file:
                audio.export(temp_file.name, format=settings.audio.file_ext)
                s3_bucket = settings.s3.bucket
                session = aioboto3.Session()
                async with session.resource("s3") as s3:
                    bucket = await s3.Bucket(s3_bucket)
                    await bucket.upload_file(temp_file.name, fs_path)

        case _:
            raise ValueError(f"Invalid file system type: {fs_type}")

    # Creates and returns a new audio entry for the file.
    return await Audio.create(
        key=key,
        name=DEFAULT_NAME if name is None else name,
        user_id=user_id,
        source=source,
        num_frames=audio.frame_count(),
        num_channels=audio.channels,
        sample_rate=audio.frame_rate,
        duration=audio.duration_seconds,
    )


async def save_audio_file(
    user_id: int,
    source: AudioSource,
    file: BinaryIO,
    filename: str | None,
) -> Audio:
    """Saves the audio file to the file system.

    Args:
        user_id: The ID of the user who uploaded the audio file.
        source: The source of the audio file.
        file: The audio file.
        filename: The name of the audio file.

    Returns:
        The row in audio table containing the audio UUID.
    """
    file_extension = _get_extension(filename, "wav")
    audio = AudioSegment.from_file(file, file_extension)
    return await _save_audio(user_id, source, filename, audio)


async def get_audio_url(audio_entry: Audio) -> tuple[str, bool]:
    """Gets the file path or URL for serving the audio file.

    Args:
        audio_entry: The row in audio table containing the audio UUID.

    Returns:
        The file path or URL for serving the audio file, along with a boolean
        indicating if it is a URL.
    """
    settings = load_settings().file
    cur_time = server_time()
    fs_type = get_fs_type()
    fs_path = _get_path(audio_entry.key)

    try:
        match fs_type:
            case "file":
                if audio_entry.url is not None:
                    return audio_entry.url, False
                audio_entry.url = fs_path
                await audio_entry.save()
                return audio_entry.url, False

            case "s3":
                if audio_entry.url is not None and audio_entry.url_expires > cur_time:
                    return audio_entry.url, True
                s3_bucket = settings.s3.bucket
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    audio_entry.url = await s3.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": s3_bucket, "Key": fs_path},
                        ExpiresIn=settings.s3.url_expiration,
                    )
                audio_entry.url_expires = cur_time + timedelta(seconds=settings.s3.url_expiration - 1)
                await audio_entry.save()
                return audio_entry.url, True

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

    except Exception:
        logger.exception("Error processing %s", audio_entry.key)
        raise


async def load_audio_array(audio_uuid: UUID) -> np.ndarray:
    """Loads the audio into a Numpy array.

    Args:
        audio_uuid: The UUID of the audio.

    Returns:
        The audio as a Numpy array.
    """
    settings = load_settings().file
    fs_type = get_fs_type()
    fs_path = _get_path(audio_uuid)

    try:
        match fs_type:
            case "file":
                audio: AudioSegment = AudioSegment.from_file(fs_path, settings.audio.file_ext)
                return np.array(audio.get_array_of_samples())

            case "s3":
                s3_bucket = settings.s3.bucket
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    obj = await s3.get_object(Bucket=s3_bucket, Key=fs_path)
                    audio = AudioSegment.from_file(obj["Body"], settings.audio.file_ext)
                    return np.array(audio.get_array_of_samples())

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

    except Exception:
        logger.exception("Error processing %s", audio_uuid)
        raise


async def save_audio_array(
    user_id: int,
    source: AudioSource,
    audio_array: np.ndarray,
) -> Audio:
    """Saves the audio array to the file system.

    Args:
        user_id: The ID of the user who uploaded the audio file.
        source: The source of the audio file.
        audio_array: The audio as a Numpy array.

    Returns:
        The row in audio table containing the audio UUID.
    """
    settings = load_settings().file
    audio = AudioSegment(
        audio_array.tobytes(),
        sample_width=settings.audio.sample_width,
        frame_rate=settings.audio.sample_rate,
        channels=settings.audio.num_channels,
    )
    return await _save_audio(user_id, source, None, audio)
