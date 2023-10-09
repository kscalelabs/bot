"""Runs tests on the user APIs."""

import pytest
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockType

from bot.api.email import OneTimePassPayload


@pytest.mark.asyncio
async def test_user_signup(app_client: TestClient, mock_send_email: MockType) -> None:
    # Using my personal email so that if the mock function starts to fail
    # I will be inudated with emails letting me know how dumb I am.
    test_email = "ben@dpsh.dev"
    login_url = "/"

    # Sends an email to the user with their one-time pass.
    response = app_client.post(
        "/users/login",
        json={
            "email": test_email,
            "login_url": login_url,
        },
    )
    assert response.status_code == 200, response.json()
    assert mock_send_email.call_count == 1

    # Uses the one-time pass to get the header.
    otp = OneTimePassPayload(email=test_email)
    response = app_client.post(
        "/users/otp",
        json={
            "payload": otp.encode(),
        },
    )
    assert response.status_code == 200, response.json()
    data = response.json()
    token = data["token"]
    token_type = data["token_type"]
    headers = {"Authorization": f"{token_type} {token}"}

    # Gets the user's profile using the token.
    response = app_client.get("/users/me", headers=headers)
    assert response.status_code == 200, response.json()
    data = response.json()
    assert data["email"] == test_email

    # Delete the user.
    response = app_client.delete("/users/myself", headers=headers)
    assert response.status_code == 200, response.json()
    assert response.json() is True
