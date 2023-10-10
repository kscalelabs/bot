"""Defines functions for managing audio files.

We use ``smart_open`` to handle the filesystem for us, which lets you
reference files using a URL-like syntax. For example, you can use
``smart_open.open("file:///path/to/file.txt")`` to open a file on the local
filesystem, or ``smart_open.open("s3://bucket/path/to/file.txt")`` to open
a file on Amazon S3.
"""

import functools
import os
import shutil
import tempfile
from typing import BinaryIO, Literal, cast, get_args
from uuid import UUID

import aioboto3
import librosa
import soundfile as sf

from bot.settings import load_settings

FSType = Literal["file", "s3"]


@functools.lru_cache()
def get_fs_type() -> FSType:
    fs_type_str = load_settings().file.fs_type
    assert fs_type_str in get_args(FSType), f"Invalid file system type in configuration: {fs_type_str}"
    return cast(FSType, fs_type_str)


def get_path(uuid: UUID) -> str:
    settings = load_settings()
    return f"{settings.file.root_dir}/{uuid}.{settings.file.audio_file_ext}"


async def save_uuid(uuid: UUID, file: BinaryIO) -> None:
    settings = load_settings().file
    target_sr, min_sr = settings.audio_sample_rate, settings.audio_min_sample_rate

    # Reads the file into memory.
    data, orig_sr = sf.read(file)
    if orig_sr < min_sr:
        raise ValueError(f"Sample rate must be at least {min_sr} Hz")

    # Resamples to the target sample rate.
    data = librosa.resample(data.T, orig_sr=orig_sr, target_sr=target_sr, res_type="kaiser_fast").T

    # Saves to the filesystem.
    ext = settings.audio_file_ext
    fs_type, fs_path = get_fs_type(), get_path(uuid)

    match fs_type:
        case "file":
            with tempfile.NamedTemporaryFile(suffix=f".{ext}", delete=False) as temp_file:
                sf.write(temp_file.name, data, target_sr, format=ext)
            shutil.move(temp_file.name, fs_path)

        case "s3":
            with tempfile.NamedTemporaryFile(suffix=f".{ext}") as temp_file:
                sf.write(temp_file.name, data, orig_sr, format="flac")
                s3_bucket = settings.s3_bucket
                async with aioboto3.resource("s3") as s3:
                    bucket = await s3.Bucket(s3_bucket)
                    await bucket.upload_file(temp_file.name, fs_path)

        case _:
            raise ValueError(f"Invalid file system type: {fs_type}")


async def delete_uuid(uuid: UUID) -> None:
    fs_type, fs_path = get_fs_type(), get_path(uuid)

    match fs_type:
        case "file":
            os.remove(fs_path)

        case "s3":
            async with aioboto3.resource("s3") as s3:
                bucket = await s3.Bucket("dpsh-audio")
                await bucket.delete_objects(Delete={"Objects": [{"Key": fs_path}]})

        case _:
            raise ValueError(f"Invalid file system type: {fs_type}")


async def queue_for_generation(orig_uuid: UUID, ref_uuid: UUID, gen_uuid: UUID) -> None:
    """Queues a pair of audio samples for generation.

    After generation is finished, we save the file to the ``gen_uuid`` path.

    Args:
        orig_uuid: The UUID of the original audio file.
        ref_uuid: The UUID of the reference audio file.
        gen_uuid: The UUID of the generated audio file.
    """