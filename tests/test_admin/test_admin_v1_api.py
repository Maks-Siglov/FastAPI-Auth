from sqlalchemy import select

import pytest
from httpx import AsyncClient

from src.api.exceptions import (
    ADMIN_BLOCK_ITSELF_EXCEPTION,
    ALREADY_BLOCKED_EXCEPTION,
    NOT_BLOCKED_EXCEPTION,
)
from src.api.v1.users.models.user import BlockUserSchema, UserResponseSchema
from src.db.models import User
from src.db.session import s
from tests.test_admin.conftest import TEST_BLOCKED_USER_EMAIL, TEST_USER_EMAIL

ADMIN_API_V1 = "/api/v1/admin"

query_params_with_expected_code = [
    ({"user_id": 1}, 200),
    ({"email": "test_admin_user@gmail.com"}, 200),
    ({"first_name": "John"}, 200),
    ({"last_name": "Doe"}, 200),
    ({"is_active": True}, 200),
    ({"is_blocked": False}, 200),
    ({"order_by": "id", "order_type": "asc"}, 200),
    ({"order_by": "id", "order_type": "desc"}, 200),
    ({"order_by": "balance", "order_type": "asc"}, 200),
    ({"order_by": "balance", "order_type": "desc"}, 200),
    ({"order_by": "updated_at", "order_type": "asc"}, 200),
    ({"order_by": "updated_at", "order_type": "desc"}, 200),
    ({}, 200),
]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query_params, expected_status", query_params_with_expected_code
)
async def test_get_users(
    async_test_admin_client: AsyncClient,
    query_params: dict,
    expected_status: int,
):
    response = await async_test_admin_client.get(
        f"{ADMIN_API_V1}/users/", params=query_params
    )

    assert response.status_code == expected_status

    assert response.json()["users"][0]

    assert UserResponseSchema.model_validate(response.json()["users"][0])


@pytest.mark.asyncio
async def test_block_user(
    async_test_admin_client: AsyncClient, test_user: User
):
    response = await async_test_admin_client.post(
        f"{ADMIN_API_V1}/block/{test_user.id}/"
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["is_blocked"] is True
    assert response_data["id"] == test_user.id
    assert BlockUserSchema.model_validate(response_data)

    my_test_user = await s.user_db.scalar(
        select(User).filter(User.email == TEST_USER_EMAIL)
    )
    assert my_test_user
    assert my_test_user.is_blocked


@pytest.mark.asyncio
async def test_admin_block_itself(
    async_test_admin_client: AsyncClient, test_admin_user: User
):
    response = await async_test_admin_client.post(
        f"{ADMIN_API_V1}/block/{test_admin_user.id}/"
    )
    assert response.status_code == ADMIN_BLOCK_ITSELF_EXCEPTION.status_code
    assert response.json()["detail"] == ADMIN_BLOCK_ITSELF_EXCEPTION.detail


@pytest.mark.asyncio
async def test_block_already_blocked_user(
    async_test_admin_client: AsyncClient, test_blocked_user: User
):
    response = await async_test_admin_client.post(
        f"{ADMIN_API_V1}/block/{test_blocked_user.id}/"
    )
    assert response.status_code == ADMIN_BLOCK_ITSELF_EXCEPTION.status_code
    assert response.json()["detail"] == ALREADY_BLOCKED_EXCEPTION.detail


@pytest.mark.asyncio
async def test_unblock_user(
    async_test_admin_client: AsyncClient, test_blocked_user: User
):
    response = await async_test_admin_client.post(
        f"{ADMIN_API_V1}/unblock/{test_blocked_user.id}/"
    )
    assert response.status_code == 200

    response_data = response.json()
    assert response_data["is_blocked"] is False
    assert response_data["id"] == test_blocked_user.id
    assert BlockUserSchema.model_validate(response_data)

    my_test_user = await s.user_db.scalar(
        select(User).filter(User.email == TEST_BLOCKED_USER_EMAIL)
    )
    assert my_test_user
    assert my_test_user.is_blocked is False


@pytest.mark.asyncio
async def test_unblock_not_blocked_user(
    async_test_admin_client: AsyncClient, test_user: User
):
    response = await async_test_admin_client.post(
        f"{ADMIN_API_V1}/unblock/{test_user.id}/"
    )
    assert response.status_code == NOT_BLOCKED_EXCEPTION.status_code
    assert response.json()["detail"] == NOT_BLOCKED_EXCEPTION.detail
