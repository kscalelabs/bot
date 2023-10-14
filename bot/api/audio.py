"""Defines functions for managing audio files."""

import functools
import logging
import shutil
import tempfile
from datetime import timedelta
from typing import BinaryIO, Literal, cast, get_args
from uuid import UUID

import aioboto3
from pydub import AudioSegment

from bot.api.model import Audio
from bot.api.utils import server_time
from bot.settings import load_settings

logger = logging.getLogger(__name__)

FSType = Literal["file", "s3"]


@functools.lru_cache()
def get_fs_type() -> FSType:
    fs_type_str = load_settings().file.fs_type
    assert fs_type_str in get_args(FSType), f"Invalid file system type in configuration: {fs_type_str}"
    return cast(FSType, fs_type_str)


def _get_path(uuid: UUID) -> str:
    settings = load_settings()
    return f"{settings.file.root_dir}/{uuid}.{settings.file.audio_file_ext}"


def _get_extension(filename: str | None, default: str) -> str:
    if filename is None:
        return default
    return filename.split(".")[-1].lower() if "." in filename else default


async def save_audio(audio_entry: Audio, file: BinaryIO, filename: str | None) -> None:
    try:
        settings = load_settings().file
        target_sr, min_sr = settings.audio_sample_rate, settings.audio_min_sample_rate

        # Resamples the audio, if necessary.
        file_extension = _get_extension(filename, "wav")
        audio: AudioSegment = AudioSegment.from_file(file, file_extension)
        if audio.frame_rate < min_sr:
            raise ValueError(f"Audio sample rate must be at least {min_sr} Hz")
        resampled_audio = audio.set_frame_rate(target_sr)

        # Checks the audio duration and number of channels.
        max_duration = settings.audio_max_duration
        if resampled_audio.duration_seconds > max_duration:
            raise ValueError(f"Audio duration must be less than {max_duration} seconds")

        # Saves to the filesystem.
        ext = settings.audio_file_ext
        fs_type, fs_path = get_fs_type(), _get_path(audio_entry.uuid)

        match fs_type:
            case "file":
                with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as temp_file:
                    resampled_audio.export(temp_file.name, format=ext)
                shutil.move(temp_file.name, fs_path)

            case "s3":
                with tempfile.NamedTemporaryFile(suffix=f".{ext}") as temp_file:
                    resampled_audio.export(temp_file.name, format=ext)
                    s3_bucket = settings.s3_bucket
                    session = aioboto3.Session()
                    async with session.resource("s3") as s3:
                        bucket = await s3.Bucket(s3_bucket)
                        await bucket.upload_file(temp_file.name, fs_path)

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

        # Updates the audio entry with the audio metadata.
        audio_entry.num_frames = resampled_audio.frame_count()
        audio_entry.num_channels = resampled_audio.channels
        audio_entry.sample_rate = resampled_audio.frame_rate
        audio_entry.duration = resampled_audio.duration_seconds
        audio_entry.available = True
        await audio_entry.save()

    except Exception:
        logger.exception("Error processing %s", audio_entry.uuid)
        await audio_entry.delete()


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
    fs_path = _get_path(audio_entry.uuid)

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
                s3_bucket = settings.s3_bucket
                session = aioboto3.Session()
                async with session.client("s3") as s3:
                    audio_entry.url = await s3.generate_presigned_url(
                        ClientMethod="get_object",
                        Params={"Bucket": s3_bucket, "Key": fs_path},
                        ExpiresIn=settings.s3_url_expiration,
                    )
                audio_entry.url_expires = cur_time + timedelta(seconds=settings.s3_url_expiration - 1)
                await audio_entry.save()
                return audio_entry.url, True

            case _:
                raise ValueError(f"Invalid file system type: {fs_type}")

    except Exception:
        logger.exception("Error processing %s", audio_entry.uuid)
        raise
