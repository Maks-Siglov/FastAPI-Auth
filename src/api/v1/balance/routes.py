from fastapi import APIRouter, Depends

from starlette import status

from src.api.exceptions import (
    insufficient_balance_error,
    negative_balance_error,
)
from src.api.v1.balance.crud import decrease_balance, increase_balance
from src.api.v1.balance.dependencies import get_user_balance
from src.api.v1.balance.models.balance import AmountSchema, UserBalanceSchema
from src.api.v1.users.dependencies import get_current_user
from src.db.models import User

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get(
    "/get/",
    description="Get user's balance",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": UserBalanceSchema},
        status.HTTP_409_CONFLICT: {
            "description": negative_balance_error.detail
        },
    },
)
def get_balance(
    balance: int = Depends(get_user_balance),
    user: User = Depends(get_current_user),
) -> UserBalanceSchema:
    return UserBalanceSchema(user_id=user.id, balance=balance)


@router.patch(
    "/deposit/",
    description="Deposit to the user's balance",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": AmountSchema},
    },
)
async def deposit_balance(
    amount_schema: AmountSchema,
    user: User = Depends(get_current_user),
) -> UserBalanceSchema:

    await increase_balance(user, amount_schema.amount)

    return UserBalanceSchema(user_id=user.id, balance=user.balance)


@router.patch(
    "/withdraw/",
    description="Withdraw from the user's balance",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_200_OK: {"model": AmountSchema},
        status.HTTP_409_CONFLICT: {
            "description": insufficient_balance_error.detail
        },
    },
)
async def withdraw_balance(
    amount_schema: AmountSchema,
    user: User = Depends(get_current_user),
) -> UserBalanceSchema:
    if user.balance < amount_schema.amount:
        raise insufficient_balance_error

    await decrease_balance(user, amount_schema.amount)

    return UserBalanceSchema(user_id=user.id, balance=user.balance)
