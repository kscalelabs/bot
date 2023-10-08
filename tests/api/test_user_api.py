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
    login_url = "/"
    payload = VerificationPayload(test_email, login_url).encode()

    response = app_client.post(
        "/users/create",
        json={
            "email": test_email,
            "password": "testpassword",
            "login_url": login_url,
        },
    )
    assert response.status_code == 200
    assert mock_send_email.call_count == 1

    # The response is a 307, which redirects to "/" API endpoint, thus the 200.
    response = app_client.get(f"/users/verify/{payload}")
    assert response.status_code == 200
