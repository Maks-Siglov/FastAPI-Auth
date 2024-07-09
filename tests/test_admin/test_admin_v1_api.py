import pytest
from httpx import AsyncClient

from src.db.models import User

ADMIN_API_V1 = "/api/v1/admin"


query_params_with_expected_code = [
    ({"user_id": 1}, 200),
    ({"email": "test_email@gmail.com"}, 200),
    ({"is_active": True}, 200),
    ({"order_by": "created_at", "desc": True}, 200),
    ({"order_by": "is_active"}, 200),
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
