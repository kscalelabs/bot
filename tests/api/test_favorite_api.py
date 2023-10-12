"""Tests the favorites API functions."""

import os

import numpy as np
import pytest
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from fastapi.testclient import TestClient


@pytest.mark.asyncio
async def test_favotires_functions(
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

    # Tests uploading some audio files to the "/make/upload" endpoint.
    upload_uuids: list[str] = []
    record_uuids: list[str] = []
    for source, uuid_list in (("uploaded", upload_uuids), ("recorded", record_uuids)):
        for _ in range(5):
            response = app_client.post(
                "/make/upload",
                files={"file": ("test.wav", audio_file_raw)},
                data={"source": source},
            )
            assert response.status_code == 200, (response.status_code, response.json())
            data = response.json()
            uuid_list.append(data["uuid"])

    # Favorites the first three.
    for uuid in upload_uuids[:3]:
        response = app_client.post("/favorites/add", json={"uuid": uuid})
        assert response.status_code == 200, response.json()
        assert response.json() is True

    # Queries the user's favorites.
    response = app_client.get("/favorites/query/me", params={"start": 0, "limit": 5})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["uuids"]) == 3
    assert data["uuids"] == upload_uuids[:3][::-1]

    # Removes the first favorite.
    response = app_client.delete("/favorites/remove", params={"uuid": upload_uuids[0]})
    assert response.status_code == 200, response.json()
    assert response.json() is True

    # Queries the user's favorites again.
    response = app_client.get("/favorites/query/me", params={"start": 0, "limit": 5})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["uuids"]) == 2
    assert data["uuids"] == upload_uuids[1:3][::-1]
