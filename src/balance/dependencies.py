from fastapi import Depends

from auth.dependencies import get_current_user
from balance.exceptions import negative_balance_error
from models import User


def get_user_balance(user: User = Depends(get_current_user)) -> int:
    if user.balance < 0:
        raise negative_balance_error

    return user.balance