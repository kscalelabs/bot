"""Tests the main API."""

from fastapi.testclient import TestClient


def test_user_signup(app_client: TestClient) -> None:
    response = app_client.get("/")
    assert response.status_code == 200


def test_run() -> None:
    assert True
