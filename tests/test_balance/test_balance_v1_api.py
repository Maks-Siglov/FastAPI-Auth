import pytest
from httpx import AsyncClient

from src.db.models import User

BALANCE_API_V1 = "/api/v1/balance"


@pytest.mark.asyncio
async def test_get_balance(
    async_test_balance_client: AsyncClient, test_user_with_balance: User
):
    response = await async_test_balance_client.get(f"{BALANCE_API_V1}/get/")

    assert response.status_code == 200

    assert response.json() == {
        "user_id": test_user_with_balance.id,
        "balance": test_user_with_balance.balance,
    }


@pytest.mark.asyncio
async def test_deposit_balance(
    async_test_balance_client: AsyncClient, test_user_with_balance: User
):
    deposit_post_data = {"amount": 200}

    response = await async_test_balance_client.post(
        f"{BALANCE_API_V1}/deposit/", json=deposit_post_data
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_withdraw_balance(
    async_test_balance_client: AsyncClient, test_user_with_balance: User
):
    deposit_post_data = {"amount": 200}

    response = await async_test_balance_client.post(
        f"{BALANCE_API_V1}/withdraw/", json=deposit_post_data
    )

    assert response.status_code == 200


@pytest.mark.asyncio
async def test_wrong_withdraw_balance(
    async_test_balance_client: AsyncClient, test_user_with_balance: User
):
    deposit_post_data = {"amount": 400}

    response = await async_test_balance_client.post(
        f"{BALANCE_API_V1}/withdraw/", json=deposit_post_data
    )

    assert response.status_code == 409
    assert (
        response.json()["detail"] == "Insufficient funds on the balance sheet"
    )
