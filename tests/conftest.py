"""Pytest configuration file."""

import functools
from typing import Generator

import pytest
import torch
from _pytest.legacypath import TempdirFactory
from _pytest.python import Function, Metafunc
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockerFixture, MockType

from bot.settings import Settings


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
    mock = mocker.patch("bot.settings.load_settings")
    settings = Settings()

    # Sets the default app settings.
    settings.is_prod = False

    # Sets the default site settings.
    settings.site.homepage = "http://localhost"

    # Sets the default database settings.
    settings.database.kind = "sqlite"
    settings.database.host = ":memory:"
    settings.database.port = None
    settings.database.path = None
    settings.database.username = None
    settings.database.password = None

    # Sets the default image settings.
    file_root_dir = tmpdir_factory.mktemp("files")
    settings.file.fs_type = "file"
    settings.file.root_dir = str(file_root_dir)

    # Sets the default email settings.
    settings.email.host = "localhost"
    settings.email.port = 587
    settings.email.name = "name"
    settings.email.email = "email"
    settings.email.password = "password"

    # Sets the default crypto settings.
    settings.crypto.jwt_secret = "jwt_secret"
    settings.crypto.expire_token_minutes = 60

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


@pytest.fixture()
def authenticated_user(app_client: TestClient) -> tuple[TestClient, str]:
    from bot.api.email import OneTimePassPayload

    test_email = "ben@dpsh.dev"

    # Logs the user in using the OTP.
    otp = OneTimePassPayload(email=test_email)
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

    # Gets a session token.
    response = app_client.post("/users/refresh")
    assert response.status_code == 200, response.json()

    return app_client, test_email
