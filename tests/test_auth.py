import pytest
from starlette.testclient import TestClient

from auth.schemas.token import TokenSchema
from db.session import set_session_pool, pop_session


async def test_signup(test_client: TestClient):
    await set_session_pool()
    signup_post_data = {
        "email": "new_user@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post("/auth/signup/", json=signup_post_data)
    assert response.status_code == 200

    await pop_session()

INVALID_SIGNUP_DATA = [
    ({"email": "string", "password": "Test_password22"}, 422),
    ({"email": "test_email2@gmail.com", "password": "no_uppercase2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "NO_LOVERCASE2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No2symbol"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No_digit"}, 422),
]


@pytest.mark.parametrize("login_data, expected_code", INVALID_SIGNUP_DATA)
async def test_invalid_signup(
    test_client: TestClient, login_data: dict[str, str], expected_code: int
):
    await set_session_pool()
    response = test_client.post("/auth/signup/", json=login_data)
    assert response.status_code == expected_code

    await pop_session()


async def test_login(test_client: TestClient):
    await set_session_pool()
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Test_password22",
    }
    response = test_client.post("/auth/login/", json=login_post_data)

    assert response.status_code == 200

    token_data = TokenSchema(**response.json())

    assert token_data.access_token is not None
    assert token_data.refresh_token is not None
    assert token_data.token_type is not None

    await pop_session()


async def test_invalid_password_login(test_client: TestClient):
    await set_session_pool()
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Wrong_password22"
    }
    response = test_client.post("/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


async def test_in_active_user_login(test_client: TestClient):
    await set_session_pool()
    login_post_data = {
        "email": "test_in_active_user@gmail.com",
        "password": "Test_password22"
    }
    response = test_client.post("/auth/login/", json=login_post_data)

    assert response.status_code == 401
    assert response.json()["detail"] == "User is not active"

    await pop_session()
