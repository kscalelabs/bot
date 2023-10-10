"""Tests the make API functions."""

import os

import numpy as np
import pytest
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_make_functions(
    authenticated_user: tuple[TestClient, str],
    tmpdir_factory: TempdirFactory,
) -> None:
    app_client, _ = authenticated_user

    # Creates a new dummy audio file.
    audio_file_data = np.random.uniform(size=(8000,)) * 2 - 1
    file_root_dir = tmpdir_factory.mktemp("files")
    audio_file_path = os.path.join(file_root_dir, "test.wav")
    sf.write(audio_file_path, audio_file_data, 24000)

    # Reads bytes into memory.
    with open(audio_file_path, "rb") as f:
        audio_file_raw = f.read()

    # Tests uploading two audio files to the "/make/upload" endpoint.
    uuids: list[str] = []
    for _ in range(2):
        response = app_client.post("/make/upload", files={"file": ("test.wav", audio_file_raw)})
        assert response.status_code == 200, (response.status_code, response.json())
        data = response.json()
        uuids.append(data["uuid"])

    # Tests running the model on the two uploaded files.
    response = app_client.post("/make/run", json={"orig_uuid": uuids[0], "ref_uuid": uuids[1]})
    assert response.status_code == 200, response.json()
    assert "gen_uuid" in response.json(), response.json()
