"""Tests the worker endpoint."""

import os

import numpy as np
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from aiohttp.test_utils import TestClient as AsyncTestClient
from fastapi.testclient import TestClient

from bot.api.email import OneTimePassPayload


async def test_worker_endpoint(
    app_client: TestClient,
    tmpdir_factory: TempdirFactory,
    infer_client: AsyncTestClient,
) -> None:
    # Logs the user in using the OTP.
    otp = OneTimePassPayload(email="ben@dpsh.dev")
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

    # Gets a session token.
    response = app_client.post("/users/refresh")
    data = response.json()
    assert response.status_code == 200, data

    # Creates a new dummy audio file.
    audio_file_data = np.random.uniform(size=(8000,)) * 2 - 1
    file_root_dir = tmpdir_factory.mktemp("files")
    audio_file_path = os.path.join(file_root_dir, "test.wav")
    sf.write(audio_file_path, audio_file_data, 24000)

    # Reads bytes into memory.
    with open(audio_file_path, "rb") as f:
        audio_file_raw = f.read()

    # Tests uploading two audio files to the "/audio/upload" endpoint.
    ids: list[str] = []
    for _ in range(2):
        response = app_client.post(
            "/audio/upload",
            files={"file": ("test.wav", audio_file_raw)},
            data={"source": "uploaded"},
        )
        assert response.status_code == 200, (response.status_code, response.json())
        data = response.json()
        ids.append(data["id"])

    # Tests calling the endpoint.
    endpoint = f"/?source_id={ids[0]}&reference_id={ids[1]}"
    response = await infer_client.get(endpoint)
    assert response.status == 200, response.json()
    data = await response.json()
    assert isinstance(data["output_id"], int)
    assert isinstance(data["generation_id"], int)
