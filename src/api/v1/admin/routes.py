import logging

from fastapi import APIRouter, Depends

from starlette import status

from src.api.exceptions import (
    ADMIN_BLOCK_ITSELF_EXCEPTION,
    ALREADY_BLOCKED_EXCEPTION,
    NOT_BLOCKED_EXCEPTION,
    NOT_FOUND,
)
from src.api.v1.admin.crud import filtered_users
from src.api.v1.admin.dependencies import check_admin_role
from src.api.v1.admin.models.admin_query_params import AdminQueryParams
from src.api.v1.users.crud import (
    block_my_user,
    get_user_by_id,
    unblock_my_user,
)
from src.api.v1.users.dependencies import get_current_user
from src.api.v1.users.models.user import (
    BlockUserSchema,
    UserResponseSchema,
    UsersResponseSchema,
)
from src.db.models import User

log = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(check_admin_role)],
)  # include_in_schema=False


@router.get(
    "/users/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": UsersResponseSchema}},
)
async def get_users(
    params: AdminQueryParams = Depends(AdminQueryParams),
) -> dict[str, list[UserResponseSchema]]:
    users = await filtered_users(params)
    return {
        "users": [UserResponseSchema.model_validate(user) for user in users]
    }


@router.post(
    "/block/{user_id}/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": BlockUserSchema}},
)
async def block_user(
    user_id: int, admin_user: User = Depends(get_current_user)
) -> BlockUserSchema:
    if (user := await get_user_by_id(user_id)) is None:
        raise NOT_FOUND
    if user.id == admin_user.id:
        raise ADMIN_BLOCK_ITSELF_EXCEPTION
    if user.is_blocked:
        raise ALREADY_BLOCKED_EXCEPTION

    await block_my_user(user)
    log.info(f"User {user.email} blocked successfully")
    return BlockUserSchema.model_validate(user)


@router.post(
    "/unblock/{user_id}/",
    status_code=status.HTTP_200_OK,
    responses={status.HTTP_200_OK: {"model": BlockUserSchema}},
)
async def unblock_user(user_id: int) -> BlockUserSchema:
    if (user := await get_user_by_id(user_id)) is None:
        raise NOT_FOUND
    if not user.is_blocked:
        raise NOT_BLOCKED_EXCEPTION

    await unblock_my_user(user)
    log.info(f"User {user.email} unblocked successfully")
    return BlockUserSchema.model_validate(user)
