from fastapi import APIRouter, Depends

from starlette import status

from auth.dependencies import get_current_user, http_bearer
from balance.dependencies import get_user_balance
from balance.exceptions import (
    insufficient_balance_error,
    negative_balance_error,
)
from balance.schemas import AmountSchema, UserBalanceSchema
from db.session import handle_session, s
from models import User

balance_router = APIRouter(
    prefix="/balance",
    tags=["balance"],
    dependencies=[Depends(http_bearer), Depends(handle_session)],
)


@balance_router.get(
    "/get/",
    response_model=None,
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


@balance_router.post(
    "/deposit/",
    response_model=None,
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
    user.balance += amount_schema.amount
    await s.user_db.commit()

    return UserBalanceSchema(user_id=user.id, balance=user.balance)


@balance_router.post(
    "/withdraw/",
    response_model=None,
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
):
    if user.balance < amount_schema.amount:
        raise insufficient_balance_error
    user.balance -= amount_schema.amount
    await s.user_db.commit()

    return UserBalanceSchema(user_id=user.id, balance=user.balance)