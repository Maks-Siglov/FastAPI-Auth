import pytest
from starlette.testclient import TestClient

from src.api.v1.auth.schemas.token import TokenSchema

API_V1 = "/api/v1"


def test_signup(test_client: TestClient):
    signup_post_data = {
        "email": "new_user@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post(
        f"{API_V1}/auth/signup/", json=signup_post_data
    )
    assert response.status_code == 201


INVALID_SIGNUP_DATA = [
    ({"email": "string", "password": "Test_password22"}, 422),
    ({"email": "test_email2@gmail.com", "password": "no_uppercase2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "NO_LOVERCASE2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No2symbol"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No_digit"}, 422),
]


@pytest.mark.parametrize("login_data, expected_code", INVALID_SIGNUP_DATA)
def test_invalid_signup(
    test_client: TestClient, login_data: dict[str, str], expected_code: int
):
    response = test_client.post(f"{API_V1}/auth/signup/", json=login_data)
    assert response.status_code == expected_code


def test_login(test_client: TestClient):
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post(f"{API_V1}/auth/login/", json=login_post_data)

    assert response.status_code == 200

    token_data = TokenSchema(**response.json())

    assert token_data.access_token is not None
    assert token_data.refresh_token is not None
    assert token_data.token_type is not None


def test_invalid_password_login(test_client: TestClient):
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Wrong_password22",
    }
    response = test_client.post(f"{API_V1}/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


def test_in_active_user_login(test_client: TestClient):
    login_post_data = {
        "email": "test_in_active_user@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post(f"{API_V1}/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "User is not active"
