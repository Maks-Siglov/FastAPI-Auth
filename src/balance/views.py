from fastapi import APIRouter, Depends

from auth.dependencies import get_current_user, http_bearer
from balance.dependencies import get_user_balance
from balance.schemas import UserBalanceSchema
from db.session import handle_session
from models import User

balance_router = APIRouter(
    prefix="/balance",
    tags=["balance"],
    dependencies=[Depends(http_bearer), Depends(handle_session)],
)


@balance_router.get("/get/")
def get_balance(
    balance: int = Depends(get_user_balance),
    user: User = Depends(get_current_user),
) -> UserBalanceSchema:
    return UserBalanceSchema(user_id=user.id, balance=balance)
