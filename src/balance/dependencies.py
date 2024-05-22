from fastapi import Depends

from src.auth.dependencies import get_current_user
from src.balance.exceptions import negative_balance_error
from src.models import User


def get_user_balance(user: User = Depends(get_current_user)) -> int:
    if user.balance < 0:
        raise negative_balance_error

    return user.balance
