from fastapi import Depends

from src.api.exceptions import NOT_FOUND
from src.api.v1.users.dependencies import get_current_user
from src.db.models import User


def check_admin_role(user: User = Depends(get_current_user)) -> None:
    if user.role != "admin":
        raise NOT_FOUND
