"""Defines functions for managing audio files."""

import functools
import logging
import os
import shutil
import tempfile
import uuid
from datetime import timedelta
from hashlib import sha1
from io import BytesIO
from typing import Literal, cast, get_args
from uuid import UUID

import aioboto3
import numpy as np
from fastapi import UploadFile
from pydub import AudioSegment

from bot.api.model import Audio, AudioSource
from bot.settings import load_settings
from bot.utils import server_time

DEFAULT_NAME = "Untitled"

logger = logging.getLogger(__name__)

FSType = Literal["file", "s3"]

AudioSegment.converter = shutil.which("ffmpeg")


@functools.lru_cache()
def get_fs_type() -> FSType:
    fs_type_str = load_settings().file.fs_type
    assert fs_type_str in get_args(FSType), f"Invalid file system type in configuration: {fs_type_str}"
    return cast(FSType, fs_type_str)


def _get_path(key: UUID) -> str:
    settings = load_settings()
    return f"{settings.file.root_dir}/{key}.{settings.file.audio.file_ext}"


async def _save_audio(user_id: int, source: AudioSource, name: str | None, audio: AudioSegment) -> Audio:
    settings = load_settings().file

    # Standardizes the audio format.
    if audio.frame_rate < settings.audio.min_sample_rate:
        raise ValueError(f"Audio sample rate must be at least {settings.audio.min_sample_rate} Hz")
    if audio.frame_rate != settings.audio.sample_rate:
        audio = audio.set_frame_rate(settings.audio.sample_rate)
    if audio.sample_width != settings.audio.sample_width:
        audio = audio.set_sample_width(settings.audio.sample_width)
    if audio.channels != settings.audio.num_channels:
        audio = audio.set_channels(settings.audio.num_channels)
    if audio.duration_seconds < settings.audio.min_duration:
        raise ValueError(f"Audio duration must be greater than {settings.audio.min_duration} seconds")
    if audio.duration_seconds > settings.audio.max_duration:
        raise ValueError(f"Audio duration must be less than {settings.audio.max_duration} seconds")

    key_bytes = sha1(uuid.NAMESPACE_OID.bytes + f"user-{user_id}".encode("utf-8") + os.urandom(16))
    key = UUID(bytes=key_bytes.digest()[:16], version=5)
    fs_type = get_fs_type()
    fs_path = _get_path(key)
    max_bytes = settings.audio.max_mb * 1024 * 1024

    match fs_type:
        case "file":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.audio.file_ext}", delete=False) as temp_file:
                audio.export(temp_file.name, format=settings.audio.file_ext)
            if os.path.getsize(temp_file.name) > max_bytes:
                raise ValueError("Audio file is too large")
            shutil.move(temp_file.name, fs_path)

        case "s3":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.audio.file_ext}") as temp_file:
                audio.export(temp_file.name, format=settings.audio.file_ext)
                if os.path.getsize(temp_file.name) > max_bytes:
                    raise ValueError("Audio file is too large")
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
    file: UploadFile,
    name: str | None = None,
) -> Audio:
    """Saves the audio file to the file system.

    Args:
        user_id: The ID of the user who uploaded the audio file.
        source: The source of the audio file.
        file: The audio file.
        name: The name of the audio file.

    Returns:
        The row in audio table.
    """
    try:
        file_format = None if file.content_type is None else file.content_type.split("/")[1]
        audio = AudioSegment.from_file(BytesIO(await file.read()), file_format)
    except Exception:
        logger.exception("Error processing %s with content type %s", file.filename, file.content_type)
        raise
    return await _save_audio(user_id, source, name, audio)


async def get_audio_url(audio_entry: Audio) -> tuple[str, bool]:
    """Gets the file path or URL for serving the audio file.

    Args:
        audio_entry: The row in audio table.

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
                updated = audio_entry.url != fs_path
                audio_entry.url = fs_path
                if updated:
                    audio_entry.url_expires = cur_time
                    await audio_entry.save()
                return fs_path, False

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
        audio: AudioSegment

        match fs_type:
            case "file":
                audio = AudioSegment.from_file(fs_path, settings.audio.file_ext)

            case "s3":
                s3_bucket = settings.s3.bucket
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    obj = await s3.get_object(Bucket=s3_bucket, Key=fs_path)
                    data = await obj["Body"].read()
                    audio_file_io = BytesIO(data)
                    audio = AudioSegment.from_file(audio_file_io, settings.audio.file_ext)

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

        return np.array(audio.get_array_of_samples())

    except Exception:
        logger.exception("Error processing %s", audio_uuid)
        raise


async def save_audio_array(
    user_id: int,
    source: AudioSource,
    audio_array: np.ndarray,
    name: str | None = None,
) -> Audio:
    """Saves the audio array to the file system.

    Args:
        user_id: The ID of the user who uploaded the audio file.
        source: The source of the audio file.
        audio_array: The audio as a Numpy array.
        name: The name of the audio file.

    Returns:
        The row in audio table containing the audio Id.
    """
    settings = load_settings().file
    audio = AudioSegment(
        audio_array.tobytes(),
        sample_width=settings.audio.sample_width,
        frame_rate=settings.audio.sample_rate,
        channels=settings.audio.num_channels,
    )
    return await _save_audio(user_id, source, name, audio)
