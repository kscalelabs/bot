"""Tests the collections API functions."""

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

    # Tests creating a collection from the recorded audio.
    for i in range(3):
        response = app_client.post("/collections/add", json={"name": "recorded", "audio_id": record_ids[i]})
        assert response.status_code == 200, (response.status_code, response.json())
        assert response.json() is True

    # Tests querying the collection.
    response = app_client.get("/collections/query/collection", params={"name": "recorded"})
    assert response.status_code == 200, (response.status_code, response.json())
    assert response.json() == {"audio_ids": record_ids[:3]}

    # Tests querying the user's collections.
    response = app_client.get("/collections/query/me")
    assert response.status_code == 200, (response.status_code, response.json())
    assert response.json() == {"names": ["recorded"]}

    # Tests checking if some audio IDs are in a given collection.
    response = app_client.post("/collections/query/ids", json={"name": "recorded", "audio_ids": record_ids})
    assert response.status_code == 200, (response.status_code, response.json())
    audio_ids = response.json()
    for row in audio_ids["ids"]:
        audio_id, in_collection = row["audio_id"], row["in_collection"]
        assert in_collection is (audio_id in record_ids[:3])

    # Tests removing an audio file from the collection.
    response = app_client.delete("/collections/remove", params={"name": "recorded", "audio_id": record_ids[0]})
    assert response.status_code == 200, (response.status_code, response.json())
    assert response.json() is True
