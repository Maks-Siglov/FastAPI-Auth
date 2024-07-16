from sqlalchemy import select

import pytest
from httpx import AsyncClient

from src.api.v1.users.models.token import (
    AccessTokenSchema,
    RevokedAccessTokenSchema,
    TokenSchema,
)
from src.api.v1.users.models.user import UserResponseSchema
from src.api.v1.users.utils.my_jwt import decode_jwt
from src.api.v1.users.utils.password import verify_password
from src.db.models import User
from src.db.session import s
from tests.test_users.conftest import (
    MOCK_USER_EMAIL,
    TEST_IN_ACTIVE_USER_EMAIL,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)

USERS_API_V1 = "/api/v1/users"


@pytest.mark.asyncio
async def test_signup(async_test_client: AsyncClient):
    signup_post_data = {
        "email": "new_user@gmail.com",
        "password": TEST_USER_PASSWORD,
        "first_name": "Test_name",
        "last_name": "Test_last_name",
    }
    response = await async_test_client.post(
        f"{USERS_API_V1}/signup/", json=signup_post_data
    )
    assert response.status_code == 201
    assert UserResponseSchema.model_validate(response.json())


INVALID_SIGNUP_DATA = [
    ({"email": "wrong_email", "password": "Test_password22"}, 422),
    ({"email": "test_email2@gmail.com", "password": "no_uppercase2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "NO_LOVERCASE2"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No2symbol"}, 422),
    ({"email": "test_email2@gmail.com", "password": "No_digit"}, 422),
]


@pytest.mark.asyncio
@pytest.mark.parametrize("login_data, expected_code", INVALID_SIGNUP_DATA)
async def test_invalid_signup(
    async_test_client: AsyncClient,
    login_data: dict[str, str],
    expected_code: int,
):
    response = await async_test_client.post(
        f"{USERS_API_V1}/signup/", json=login_data
    )
    assert response.status_code == expected_code


@pytest.mark.asyncio
async def test_login(async_test_client: AsyncClient, test_users: None):
    login_data = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    response = await async_test_client.post(
        f"{USERS_API_V1}/login/", json=login_data
    )

    assert response.status_code == 200

    assert TokenSchema(**response.json())


@pytest.mark.asyncio
async def test_invalid_password_login(async_test_client: AsyncClient):
    login_post_data = {
        "email": TEST_USER_EMAIL,
        "password": "Wrong_password22",
    }
    response = await async_test_client.post(
        f"{USERS_API_V1}/login/", json=login_post_data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid user credentials"


@pytest.mark.asyncio
async def test_in_active_user_login(
    async_test_client: AsyncClient, test_users: None
):
    login_post_data = {
        "email": TEST_IN_ACTIVE_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
    }
    response = await async_test_client.post(
        f"{USERS_API_V1}/login/", json=login_post_data
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "User is not active"


@pytest.mark.asyncio
async def test_logout(
    async_test_client: AsyncClient, test_access_token: str | None
):
    async_test_client.headers["Authorization"] = f"Bearer {test_access_token}"

    response = await async_test_client.post(f"{USERS_API_V1}/logout/")

    assert response.status_code == 200

    response_data = response.json()
    assert RevokedAccessTokenSchema(**response_data)
    assert response_data["revoked"]

    revoked_token = response_data["access_token"]
    token_bytes = revoked_token.encode("utf-8")

    assert decode_jwt(token_bytes)["token_revoked"]


@pytest.mark.asyncio
async def test_refresh(
    async_test_client: AsyncClient, test_access_token: str | None
):
    async_test_client.headers["Authorization"] = f"Bearer {test_access_token}"
    response = await async_test_client.post(f"{USERS_API_V1}/refresh/")

    assert response.status_code == 201
    assert AccessTokenSchema(**response.json())


@pytest.mark.asyncio
async def test_deactivate_user(
    async_test_client: AsyncClient,
    test_access_token: str | None,
    test_mock_user: User,
):
    async_test_client.headers["Authorization"] = f"Bearer {test_access_token}"
    response = await async_test_client.post(f"{USERS_API_V1}/deactivate/")

    assert response.status_code == 200

    response_data = response.json()
    assert UserResponseSchema.model_validate(response_data)
    assert response_data["is_active"] is False

    mock_user = await s.user_db.scalar(
        select(User).filter(User.email == MOCK_USER_EMAIL)
    )
    assert mock_user
    assert mock_user.is_active is False


wrong_change_password_data = [
    (
        {
            "old_password": "Wrong_password",  # old password is wrong
            "new_password": "My_new_password22",
            "new_password_confirm": "My_new_password22",
        },
        401,
    ),
    (
        {
            "old_password": "Test_password22",
            "new_password": "My_new_password22",  # new passwords not match
            "new_password_confirm": "No_match_password22",
        },
        422,
    ),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "wrong_data, expected_status", wrong_change_password_data
)
async def test_fail_change_password(
    async_test_client: AsyncClient,
    test_access_token: str | None,
    wrong_data: dict,
    expected_status: int,
):
    async_test_client.headers["Authorization"] = f"Bearer {test_access_token}"

    response = await async_test_client.post(
        f"{USERS_API_V1}/change-password/", json=wrong_data
    )

    assert response.status_code == expected_status


@pytest.mark.asyncio
async def test_change_password(
    async_test_client: AsyncClient,
    test_access_token: str | None,
):
    async_test_client.headers["Authorization"] = f"Bearer {test_access_token}"

    test_change_password_data = {
        "old_password": TEST_USER_PASSWORD,
        "new_password": "New_password22",
        "new_password_confirm": "New_password22",
    }

    response = await async_test_client.post(
        f"{USERS_API_V1}/change-password/", json=test_change_password_data
    )

    assert response.status_code == 200
    assert UserResponseSchema.model_validate(response.json())

    test_user = await s.user_db.scalar(
        select(User).filter(User.email == MOCK_USER_EMAIL)
    )
    assert test_user
    assert verify_password(
        password=test_change_password_data["new_password"],
        hashed_password=test_user.password,
    )


@pytest.mark.asyncio
async def test_get_user(async_test_client: AsyncClient):
    response = await async_test_client.get(f"{USERS_API_V1}/me/")
    assert response.status_code == 200
    assert UserResponseSchema.model_validate(response.json())
