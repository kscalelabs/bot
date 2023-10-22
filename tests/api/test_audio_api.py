"""Tests the audio API functions."""

import os

import numpy as np
import soundfile as sf
from _pytest.legacypath import TempdirFactory
from fastapi.testclient import TestClient


async def test_audio_functions(
    authenticated_user: tuple[TestClient, str, str],
    tmpdir_factory: TempdirFactory,
) -> None:
    app_client, _, token = authenticated_user

    # Creates a new dummy audio file.
    audio_file_data = np.random.uniform(size=(8000,)) * 2 - 1
    file_root_dir = tmpdir_factory.mktemp("files")
    audio_file_path = os.path.join(file_root_dir, "test.wav")
    sf.write(audio_file_path, audio_file_data, 24000)

    # Reads bytes into memory.
    with open(audio_file_path, "rb") as f:
        audio_file_raw = f.read()

    # Tests uploading some audio files to the "/audio/upload" endpoint.
    upload_ids: list[int] = []
    record_ids: list[int] = []
    for source, id_list in (("uploaded", upload_ids), ("recorded", record_ids)):
        for _ in range(5):
            response = app_client.post(
                "/audio/upload",
                files={"file": ("test.wav", audio_file_raw)},
                data={"source": source},
            )
            assert response.status_code == 200, (response.status_code, response.json())
            data = response.json()
            id_list.append(data["id"])

    # Tests querying the audio files for the user.
    for source, id_list in (("uploaded", upload_ids), ("recorded", record_ids)):
        response = app_client.get("/audio/query/me", params={"start": 0, "limit": 5, "source": source})
        assert response.status_code == 200, response.json()
        data = response.json()
        assert data["ids"] == id_list[::-1]

    # Gets the URL for a sample.
    response = app_client.get(f"/audio/media/{id_list[0]}.flac", params={"access_token": token})
    assert response.status_code == 200, response.json()

    # Gets information about the uploaded audio samples.
    response = app_client.post("/audio/query/ids", json={"ids": upload_ids})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 5

    # Updates the name for a sample.
    response = app_client.post("/audio/update", json={"id": upload_ids[0], "name": "test"})
    assert response.status_code == 200, response.json()

    # Makes some samples public.
    for i in range(2):
        response = app_client.post("/admin/act/content", json={"id": upload_ids[i], "public": True})
        assert response.status_code == 200, response.json()

    # Tests getting some random public samples.
    response = app_client.post("/audio/public", json={"count": 2})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 2
    assert {d["id"] for d in data["infos"]} == set(upload_ids[:2])

    # Deletes a sample.
    response = app_client.delete("/audio/delete", params={"id": upload_ids[0]})
    assert response.status_code == 200, response.json()

    # Gets information about the uploaded audio samples.
    response = app_client.post("/audio/query/ids", json={"ids": upload_ids})
    assert response.status_code == 200, response.json()
    data = response.json()
    assert len(data["infos"]) == 4
