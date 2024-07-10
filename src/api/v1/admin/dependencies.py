from fastapi import Depends

from src.api.exceptions import not_admin_user_role_exception
from src.api.v1.auth.dependencies import get_current_user
from src.db.models import User


def check_admin_role(user: User = Depends(get_current_user)) -> None:
    if user.role != "admin":
        raise not_admin_user_role_exception
