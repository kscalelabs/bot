"""Runs tests on the user APIs."""

import pytest
from fastapi.testclient import TestClient
from pytest_mock.plugin import MockType


@pytest.mark.asyncio
async def test_user_signup(app_client: TestClient, mock_send_email: MockType) -> None:
    from bot.api.email import VerificationPayload

    # Using my personal email so that if the mock function starts to fail
    # I will be inudated with emails letting me know how dumb I am.
    test_email = "ben@dpsh.dev"
    test_password = "testpassword"
    login_url = "/"
    payload = VerificationPayload(test_email, login_url).encode()

    response = app_client.post(
        "/users/create",
        json={
            "email": test_email,
            "password": test_password,
            "login_url": login_url,
        },
    )
    assert response.status_code == 200
    assert mock_send_email.call_count == 1

    # The response is a 307, which redirects to "/" API endpoint, thus the 200.
    response = app_client.get(f"/users/verify/{payload}")
    assert response.status_code == 200

    # Logs the user in.
    response = app_client.post(
        "/users/login",
        json={
            "email": test_email,
            "password": test_password,
        },
    )
    assert response.status_code == 200
    data = response.json()
    token = data["token"]
    token_type = data["token_type"]
    assert token_type == "bearer"

    # Gets the user's profile using the token.
    response = app_client.get("/users/me", headers={"Authorization": f"{token_type} {token}"})
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == test_email
    assert data["email_verified"] is True
