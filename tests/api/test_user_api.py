"""Runs tests on the user APIs."""

from fastapi.testclient import TestClient
from pytest_mock.plugin import MockType

from bot.api.email import OneTimePassPayload


def test_user_auth_functions(app_client: TestClient, mock_send_email: MockType) -> None:
    # Using my personal email so that if the mock function starts to fail
    # I will be inudated with emails letting me know how dumb I am.
    # This is set as an admin email in the test settings.
    test_email = "ben@dpsh.dev"
    login_url = "/"
    bad_actor_email = "badactor@gmail.com"

    # Creates a bad actor user for testing admin actions later.
    otp = OneTimePassPayload(email=bad_actor_email)
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

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

    # Uses the one-time pass to set client cookies.
    otp = OneTimePassPayload(email=test_email)
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

    # Checks that we get a 401 without a session token.
    response = app_client.get("/users/me")
    assert response.status_code == 401, response.json()
    assert response.json()["detail"] == "Not authenticated"

    # Get a session token.
    response = app_client.post("/users/refresh")
    assert response.status_code == 200, response.json()
    assert response.json()["token_type"] == "Bearer"

    # Gets the user's profile using the token.
    response = app_client.get("/users/me")
    assert response.status_code == 200, response.json()
    assert response.json()["email"] == test_email

    # Log the user out.
    response = app_client.delete("/users/logout")
    assert response.status_code == 200, response.json()
    assert response.json() is True

    # Check that the user cookie has been cleared.
    response = app_client.get("/users/me")
    assert response.status_code == 401, response.json()
    assert response.json()["detail"] == "Not authenticated"

    # Log the user back in.
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 200, response.json()

    # Gets another session token.
    response = app_client.post("/users/refresh")
    assert response.status_code == 200, response.json()

    # Checks the current user is an admin account.
    response = app_client.get("/admin/check")
    assert response.status_code == 200, response.json()
    assert response.json() is True

    # Tests admin actions.
    response = app_client.post("/admin/act/user", json={"email": bad_actor_email, "banned": True})
    assert response.status_code == 200, response.json()

    # Tests logging in the bad actor user again, to make sure it's banned.
    otp = OneTimePassPayload(email=bad_actor_email)
    response = app_client.post("/users/otp", json={"payload": otp.encode()})
    assert response.status_code == 401, response.json()
    assert response.json()["detail"] == "User is not allowed to log in"

    # Delete the user.
    response = app_client.delete("/users/me")
    assert response.status_code == 200, response.json()
    assert response.json() is True

    # Make sure the user is gone.
    response = app_client.get("/users/me")
    assert response.status_code == 400, response.json()
    assert response.json()["detail"] == "User not found"
