import pytest
from httpx import AsyncClient

from src.db.models import User

ADMIN_API_V1 = "/api/v1/admin"


@pytest.mark.asyncio
async def test_get_users(
    async_test_admin_client: AsyncClient,
    test_admin_user: User,
):

    response = await async_test_admin_client.get(
        f"{ADMIN_API_V1}/users/",
    )

    assert response.status_code == 200
