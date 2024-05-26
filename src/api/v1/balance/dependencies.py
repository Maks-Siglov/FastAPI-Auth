from fastapi import Depends

from src.api.v1.auth.dependencies import get_current_user
from src.db.models import User
from src.api.exceptions import negative_balance_error


def get_user_balance(user: User = Depends(get_current_user)) -> int:
    if user.balance < 0:
        raise negative_balance_error

    return user.balance
