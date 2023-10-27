"""Defines functions for managing audio files."""

import functools
import logging
import mimetypes
import os
import shutil
import tempfile
import uuid
from hashlib import sha1
from io import BytesIO
from pathlib import Path
from typing import Literal, cast, get_args
from uuid import UUID

import aioboto3
import numpy as np
from fastapi import UploadFile
from pydub import AudioSegment

from bot.api.model import Audio, AudioSource
from bot.settings import settings

DEFAULT_NAME = "Untitled"

logger = logging.getLogger(__name__)

FSType = Literal["file", "s3"]

AudioSegment.converter = shutil.which("ffmpeg")


@functools.lru_cache()
def get_fs_type() -> FSType:
    fs_type_str = settings.file.fs_type
    assert fs_type_str in get_args(FSType), f"Invalid file system type in configuration: {fs_type_str}"
    return cast(FSType, fs_type_str)


def _get_file_path(key: UUID) -> str:
    (dir_path := Path(settings.file.local.root_dir).expanduser().resolve()).mkdir(parents=True, exist_ok=True)
    return str(dir_path / f"{key}.{settings.file.audio.file_ext}")


def _get_s3_path(key: UUID) -> str:
    return f"{settings.file.s3.subfolder}/{key}.{settings.file.audio.file_ext}"


async def _save_audio(user_id: int, source: AudioSource, name: str | None, audio: AudioSegment) -> Audio:
    # Standardizes the audio format.
    if audio.frame_rate < settings.file.audio.min_sample_rate:
        raise ValueError(
            f"Audio sample rate must be at least {settings.file.audio.min_sample_rate} frames per second, "
            f"got {audio.frame_rate} frames per second"
        )
    if audio.frame_rate != settings.file.audio.sample_rate:
        audio = audio.set_frame_rate(settings.file.audio.sample_rate)
    if audio.sample_width != settings.file.audio.sample_width:
        audio = audio.set_sample_width(settings.file.audio.sample_width)
    if audio.channels != settings.file.audio.num_channels:
        audio = audio.set_channels(settings.file.audio.num_channels)
    if audio.duration_seconds < settings.file.audio.min_duration:
        raise ValueError(
            f"Audio duration must be greater than {settings.file.audio.min_duration} seconds, "
            f"got {audio.duration_seconds} seconds"
        )
    if audio.duration_seconds > settings.file.audio.max_duration:
        raise ValueError(
            f"Audio duration must be less than {settings.file.audio.max_duration} seconds, "
            f"got {audio.duration_seconds} seconds"
        )

    key_bytes = sha1(uuid.NAMESPACE_OID.bytes + f"user-{user_id}".encode("utf-8") + os.urandom(16))
    key = UUID(bytes=key_bytes.digest()[:16], version=5)
    fs_type = get_fs_type()
    max_bytes = settings.file.audio.max_mb * 1024 * 1024

    match fs_type:
        case "file":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.file.audio.file_ext}", delete=False) as temp_file:
                audio.export(temp_file.name, format=settings.file.audio.file_ext)
            if os.path.getsize(temp_file.name) > max_bytes:
                raise ValueError("Audio file is too large")
            shutil.move(temp_file.name, _get_file_path(key))

        case "s3":
            with tempfile.NamedTemporaryFile(suffix=f".{settings.file.audio.file_ext}") as temp_file:
                audio.export(temp_file.name, format=settings.file.audio.file_ext)
                if os.path.getsize(temp_file.name) > max_bytes:
                    raise ValueError("Audio file is too large")
                s3_bucket = settings.file.s3.bucket
                session = aioboto3.Session()
                async with session.resource("s3") as s3:
                    bucket = await s3.Bucket(s3_bucket)
                    await bucket.upload_file(temp_file.name, _get_s3_path(key))

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


def get_file_format(content_type: str | None) -> str | None:
    if content_type is None:
        return None
    match content_type.strip().lower().split(";", 1)[0]:
        case "audio/wav":
            return "wav"
        case "audio/x-wav":
            return "wav"
        case "audio/mpeg":
            return "mp3"
        case "audio/mp3":
            return "mp3"
        case "audio/webm":
            return "webm"
        case "audio/x-webm":
            return "webm"
        case "audio/mp4":
            return "mp4"
        case "audio/ogg":
            return "ogg"
        case "audio/x-ogg":
            return "ogg"
        case "audio/flac":
            return "flac"
        case "audio/x-flac":
            return "flac"
        case "audio/x-m4a":
            return "m4a"
        case "audio/aac":
            return "aac"
        case "audio/x-aac":
            return "aac"
    ext = mimetypes.guess_extension(content_type)
    if ext is not None:
        return ext[1:]
    return None


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
    fmt = get_file_format(file.content_type)
    with tempfile.NamedTemporaryFile(suffix=f".{'wav' if fmt is None else fmt}") as temp_file:
        temp_file.write(await file.read())
        temp_file.flush()
        try:
            audio = AudioSegment.from_file(temp_file.name, fmt)
        except Exception:
            logger.exception("Error processing %s with format %s (%s)", file.filename, fmt, file.content_type)
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
    fs_type = get_fs_type()

    try:
        match fs_type:
            case "file":
                fs_path = _get_file_path(audio_entry.key)
                return fs_path, False

            case "s3":
                s3_path = _get_s3_path(audio_entry.key)
                s3_bucket = settings.file.s3.bucket
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    url = await s3.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": s3_bucket, "Key": s3_path},
                        ExpiresIn=settings.file.s3.url_expiration,
                    )
                return url, True

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
    fs_type = get_fs_type()

    try:
        audio: AudioSegment

        match fs_type:
            case "file":
                fs_path = _get_file_path(audio_uuid)
                audio = AudioSegment.from_file(fs_path, settings.file.audio.file_ext)

            case "s3":
                s3_bucket = settings.file.s3.bucket
                s3_path = _get_s3_path(audio_uuid)
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    obj = await s3.get_object(Bucket=s3_bucket, Key=s3_path)
                    data = await obj["Body"].read()
                    audio_file_io = BytesIO(data)
                    audio = AudioSegment.from_file(audio_file_io, settings.file.audio.file_ext)

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
    audio = AudioSegment(
        audio_array.tobytes(),
        sample_width=settings.file.audio.sample_width,
        frame_rate=settings.file.audio.sample_rate,
        channels=settings.file.audio.num_channels,
    )
    return await _save_audio(user_id, source, name, audio)


async def delete_audio(key: UUID) -> None:
    """Deletes the audio file from the file system.

    Args:
        key: The UUID of the audio file to delete
    """
    fs_type = get_fs_type()

    try:
        match fs_type:
            case "file":
                fs_path = _get_file_path(key)
                os.remove(fs_path)

            case "s3":
                s3_bucket = settings.file.s3.bucket
                s3_path = _get_s3_path(key)
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    await s3.delete_object(Bucket=s3_bucket, Key=s3_path)

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

    except Exception:
        logger.exception("Error processing %s", key)
        raise
