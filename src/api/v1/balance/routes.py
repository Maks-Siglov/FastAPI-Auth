from fastapi import APIRouter, Depends

from starlette import status

from src.api.v1.auth.dependencies import get_current_user
from src.api.v1.balance.dependencies import get_user_balance
from src.api.v1.balance.schemas import AmountSchema, UserBalanceSchema
from src.db.models import User
from src.db.session import s
from src.api.exceptions import insufficient_balance_error, negative_balance_error

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get(
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


@router.post(
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


@router.post(
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
