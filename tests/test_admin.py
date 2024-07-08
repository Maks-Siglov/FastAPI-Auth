import pytest
from httpx import AsyncClient

from src.db.models import User

ADMIN_API_V1 = "/api/v1/admin"


@pytest.mark.asyncio
async def test_get_users(
    a_test_client: AsyncClient,
    test_admin_user: User,
    test_admin_user_token: str,
):
    a_test_client.headers["Authorization"] = f"Bearer {test_admin_user_token}"
    response = await a_test_client.get(
        f"{ADMIN_API_V1}/users/",
    )

    print(a_test_client.headers)

    assert response.status_code == 200
