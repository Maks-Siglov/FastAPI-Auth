import pytest
from httpx import AsyncClient

from src.api.v1.auth.models.token import TokenSchema

API_V1 = "/api/v1"


@pytest.mark.asyncio
async def test_signup(a_test_client: AsyncClient):
    signup_post_data = {
        "email": "new_user@gmail.com",
        "password": "Test_password22",
    }
    response = await a_test_client.post(
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


@pytest.mark.asyncio
@pytest.mark.parametrize("login_data, expected_code", INVALID_SIGNUP_DATA)
async def test_invalid_signup(
    a_test_client: AsyncClient, login_data: dict[str, str], expected_code: int
):
    response = await a_test_client.post(
        f"{API_V1}/auth/signup/", json=login_data
    )
    assert response.status_code == expected_code


@pytest.mark.asyncio
async def test_invalid_password_login(a_test_client: AsyncClient):
    login_post_data = {
        "email": "test_email@gmail.com",
        "password": "Wrong_password22",
    }
    response = await a_test_client.post(
        f"{API_V1}/auth/login/", json=login_post_data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


@pytest.mark.asyncio
async def test_in_active_user_login(a_test_client: AsyncClient, test_user):
    login_post_data = {
        "email": "test_in_active_user@gmail.com",
        "password": "Test_password22",
    }
    response = await a_test_client.post(
        f"{API_V1}/auth/login/", json=login_post_data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User is not active"
