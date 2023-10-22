"""Pytest configuration file."""

import functools
import os
import uuid
from typing import AsyncGenerator, Callable, Generator

import pytest
import torch
import yarl
from _pytest.legacypath import TempdirFactory
from _pytest.python import Function, Metafunc
from aiohttp.test_utils import TestClient as AsyncTestClient
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture, MockType

os.environ["DPSH_ENVIRONMENT"] = "test"


@functools.lru_cache()
def has_gpu() -> bool:
    return torch.cuda.is_available()


def pytest_runtest_setup(item: Function) -> None:
    for mark in item.iter_markers():
        if mark.name == "has_gpu" and not has_gpu():
            pytest.skip("Skipping because this test requires a GPU and none is available")


def pytest_collection_modifyitems(items: list[Function]) -> None:
    items.sort(key=lambda x: x.get_closest_marker("slow") is not None)


def pytest_generate_tests(metafunc: Metafunc) -> None:
    if "device" in metafunc.fixturenames:
        torch_devices = [torch.device("cpu")]
        if has_gpu():
            torch_devices.append(torch.device("cuda"))
        metafunc.parametrize("device", torch_devices)


@pytest.fixture(scope="function", autouse=True)
def mock_load_settings(mocker: MockerFixture, tmpdir_factory: TempdirFactory) -> MockType:
    mock = mocker.patch("bot.settings._load_environment_settings")

    from bot.settings import env_settings as settings

    # Sets the default image settings.
    file_root_dir = tmpdir_factory.mktemp("files")
    settings.file.root_dir = str(file_root_dir)

    mock.return_value = settings

    return mock


@pytest.fixture(autouse=True)
def mock_send_email(mocker: MockerFixture) -> MockType:
    mock = mocker.patch("bot.api.email.send_email")
    mock.return_value = None
    return mock


@pytest.fixture()
def app_client() -> Generator[TestClient, None, None]:
    from bot.api.app.main import app

    with TestClient(app) as app_client:
        yield app_client


@pytest.fixture(autouse=True)
async def mock_call_infer_backend(mocker: MockerFixture) -> MockType:
    from bot.api.model import Audio, AudioSource, Generation

    mock = mocker.patch("bot.api.app.infer.make_request")

    async def mock_fn(endpoint: str) -> dict[str, int]:
        url = yarl.URL(endpoint)
        source_id = int(url.query["source_id"])
        reference_id = int(url.query["reference_id"])

        source, reference = await Audio.get(id=source_id), await Audio.get(id=reference_id)

        output = await Audio.create(
            key=uuid.uuid4(),
            name="test",
            user_id=source.user_id,
            source=AudioSource.generated,
            num_frames=100,
            num_channels=1,
            sample_rate=16000,
            duration=1.0,
        )

        generation = await Generation.create(
            user_id=source.user_id,
            source=source,
            reference=reference,
            output=output,
            model="test",
            elapsed_time=1.0,
        )

        return {"output_id": output.id, "generation_id": generation.id}

    mock.side_effect = mock_fn

    return mock


@pytest.fixture()
async def infer_client(mocker: MockerFixture, aiohttp_client: Callable) -> AsyncGenerator[AsyncTestClient, None]:
    from bot.worker.server import Server

    async with Server() as server:
        yield await aiohttp_client(server.app)


@pytest.fixture()
def authenticated_user(app_client: TestClient) -> tuple[TestClient, str, str]:
    from bot.api.email import OneTimePassPayload

    test_email = "ben@dpsh.dev"

    # Logs the user in using the OTP.
    otp = OneTimePassPayload(email=test_email)
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

    # Gets a session token.
    response = app_client.post("/users/refresh")
    data = response.json()
    assert response.status_code == 200, data

    return app_client, test_email, data["token"]
