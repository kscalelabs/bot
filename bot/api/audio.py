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
from typing import Literal, cast, get_args

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


def get_path(uuid: str) -> str:
    settings = load_settings()
    return f"{settings.file.root_dir}/{uuid}.{settings.file.audio_file_ext}"


async def save_uuid(uuid: str, file: sf.SoundFile) -> None:
    settings = load_settings().file
    sr, min_sr = settings.audio_sample_rate, settings.audio_min_sample_rate
    if file.samplerate < min_sr:
        raise ValueError(f"Sample rate must be at least {min_sr} Hz, got {file.samplerate}")

    # Resamples to the target sample rate.
    data = file.read()
    data = librosa.resample(data, orig_sr=file.samplerate, target_sr=sr)

    # Saves to a temporary file.
    ext = settings.audio_file_ext
    fs_type, fs_path = get_fs_type(), get_path(uuid)
    temp_file = tempfile.NamedTemporaryFile(suffix=f".{ext}")
    sf.write(temp_file.name, data, sr, format="flac")

    match fs_type:
        case "file":
            # Since we're just moving it, we don't need to delete it afterwards.
            shutil.move(temp_file.name, fs_path)

        case "s3":
            s3_bucket = settings.s3_bucket
            async with aioboto3.resource("s3") as s3:
                bucket = await s3.Bucket(s3_bucket)
                await bucket.upload_file(temp_file.name, fs_path)
            temp_file.close()

        case _:
            raise ValueError(f"Invalid file system type: {fs_type}")


async def delete_uuid(uuid: str) -> None:
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


async def queue_for_generation(orig_uuid: str, ref_uuid: str, gen_uuid: str) -> None:
    """Queues a pair of audio samples for generation.

    After generation is finished, we save the file to the ``gen_uuid`` path.

    Args:
        orig_uuid: The UUID of the original audio file.
        ref_uuid: The UUID of the reference audio file.
        gen_uuid: The UUID of the generated audio file.
    """
