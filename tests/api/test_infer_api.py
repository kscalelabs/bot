"""Tests the generation API functions."""

import os

import numpy as np
import pytest
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_generation_functions(
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

    # Tests running the model on the two uploaded files.
    gen_ids: list[str] = []
    for _ in range(3):
        response = app_client.post("/infer/run", json={"source_id": ids[0], "reference_id": ids[1]})
        assert response.status_code == 200, response.json()
        data = response.json()
        gen_ids.append(data["id"])

    # Makes some generations public.
    for i in range(2):
        response = app_client.post("/admin/act/generation", json={"id": gen_ids[i], "public": True})
        assert response.status_code == 200, response.json()

    # Tests getting some random public generations.
    response = app_client.post("/generation/public", json={"count": 2})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 2
    assert {d["id"] for d in data["infos"]} == set(gen_ids[:2])

    # Queries the number of generations.
    response = app_client.get("/generation/info/me")
    assert response.status_code == 200, response.json()
    assert response.json()["count"] == 3

    # Queries the generations.
    response = app_client.get("/generation/query/me", params={"start": 0, "limit": 5})
    assert response.status_code == 200, response.json()
    assert len(response.json()["generations"]) == 3
