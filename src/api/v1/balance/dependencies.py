from fastapi import Depends

from src.api.exceptions import NEGATIVE_BALANCE_ERROR
from src.api.v1.users.dependencies import get_current_user
from src.db.models import User


def get_user_balance(user: User = Depends(get_current_user)) -> int:
    if user.balance < 0:
        raise NEGATIVE_BALANCE_ERROR

    return user.balance
