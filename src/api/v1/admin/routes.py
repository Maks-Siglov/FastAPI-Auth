from fastapi import APIRouter, Depends

from starlette import status

from src.api.v1.admin.crud import filtered_users
from src.api.v1.admin.models import AdminQueryParams
from src.api.v1.auth.models.user import (
    UserResponseSchema,
    UsersResponseSchema,
)

router = APIRouter(prefix="/admin", tags=["admin"])  # include_in_schema=False


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
