import pytest
from httpx import AsyncClient

from src.db.models import User

ADMIN_API_V1 = "/api/v1/admin"


query_params_with_expected_code = [
    ({"user_id": 1}, 200),
    ({"email": "test_admin_user@gmail.com"}, 200),
    ({"first_name": "John"}, 200),
    ({"last_name": "Doe"}, 200),
    ({"is_active": True}, 200),
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
    test_admin_user: User,
    query_params: dict,
    expected_status: int,
):

    response = await async_test_admin_client.get(
        f"{ADMIN_API_V1}/users/", params=query_params
    )

    assert response.status_code == expected_status

    assert response.json()["users"][0]

    test_user = response.json()["users"][0]
    assert test_user["email"] == test_admin_user.email
    assert test_user["first_name"] == test_admin_user.first_name
    assert test_user["last_name"] == test_admin_user.last_name
    assert test_user["is_active"] == test_admin_user.is_active
    assert test_user["balance"] == test_admin_user.balance
