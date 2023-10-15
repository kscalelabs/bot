"""Tests the audio API functions."""

import os

import numpy as np
import pytest
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_audio_functions(
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

    # Tests uploading some audio files to the "/audio/upload" endpoint.
    upload_uuids: list[str] = []
    record_uuids: list[str] = []
    for source, uuid_list in (("uploaded", upload_uuids), ("recorded", record_uuids)):
        for _ in range(5):
            response = app_client.post(
                "/audio/upload",
                files={"file": ("test.wav", audio_file_raw)},
                data={"source": source},
            )
            assert response.status_code == 200, (response.status_code, response.json())
            data = response.json()
            uuid_list.append(data["uuid"])

    # Gets the info for the current user.
    response = app_client.get("/audio/info/me", params={"q": "test"})
    assert response.status_code == 200, response.json()
    assert response.json()["count"] == 10

    # Tests querying the audio files for the user.
    for source, uuid_list in (("uploaded", upload_uuids), ("recorded", record_uuids)):
        response = app_client.get("/audio/query/me", params={"start": 0, "limit": 5, "source": source})
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["uuids"] == uuid_list[::-1]

    # Gets the URL for a sample.
    response = app_client.get(f"/audio/media/{uuid_list[0]}.flac")
    assert response.status_code == 200, response.json()

    # Gets information about the uploaded audio samples.
    response = app_client.post("/audio/query/ids", json={"uuids": upload_uuids})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 5

    # Updates the name for a sample.
    response = app_client.post("/audio/update", json={"uuid": upload_uuids[0], "name": "test"})
    assert response.status_code == 200, response.json()

    # Makes some samples public.
    for i in range(2):
        response = app_client.post("/admin/act/content", json={"uuid": upload_uuids[i], "public": True})
        assert response.status_code == 200, response.json()

    # Tests getting some random public samples.
    response = app_client.post("/audio/public", json={"count": 2})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 2
    assert {d["uuid"] for d in data["infos"]} == set(upload_uuids[:2])

    # Deletes a sample.
    response = app_client.delete("/audio/delete", params={"uuid": upload_uuids[0]})
    assert response.status_code == 200, response.json()

    # Gets information about the uploaded audio samples.
    response = app_client.post("/audio/query/ids", json={"uuids": upload_uuids})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 4
